from nets.ssd import get_ssd
from nets.ssd_training import Generator,MultiBoxLoss
from utils.config import Config
from torchsummary import summary
from torch.autograd import Variable
import torch.backends.cudnn as cudnn
import time
import torch
import numpy as np
import torch.nn as nn
import torch.optim as optim
import torch.nn.init as init
def adjust_learning_rate(optimizer, lr, gamma, step):
    lr = lr * (gamma ** (step))
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr
    return lr

if __name__ == "__main__":
    Batch_size = 16
    lr = 1e-5
    Epoch = 50
    Cuda = True
    Start_iter = 0
    # 需要使用device来指定网络在GPU还是CPU运行
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = get_ssd("train",Config["num_classes"])

    print('Loading weights into state dict...')
    model_dict = model.state_dict()
    pretrained_dict = torch.load("model_data/ssd_weights.pth")
    pretrained_dict = {k: v for k, v in pretrained_dict.items() if np.shape(model_dict[k]) ==  np.shape(v)}
    model_dict.update(pretrained_dict)
    model.load_state_dict(model_dict)
    print('Finished!')

    net = model
    if Cuda:
        net = torch.nn.DataParallel(model)
        cudnn.benchmark = True
        net = net.cuda()

    annotation_path = '2007_train.txt'
    with open(annotation_path) as f:
        lines = f.readlines()
    np.random.seed(10101)
    np.random.shuffle(lines)
    np.random.seed(None)
    num_train = len(lines)

    gen = Generator(Batch_size, lines,
                    (Config["min_dim"], Config["min_dim"]), Config["num_classes"]).generate()


    optimizer = optim.Adam(net.parameters(), lr=lr)
    criterion = MultiBoxLoss(Config['num_classes'], 0.5, True, 0, True, 3, 0.5,
                             False, Cuda)

    net.train()


    epoch_size = num_train // Batch_size
    for epoch in range(Start_iter, Epoch):
        if epoch % 10 == 0:
            adjust_learning_rate(optimizer, lr, 0.95, epoch)
        loc_loss = 0
        conf_loss = 0
        for iteration in range(epoch_size):
            images, targets = next(gen)
            with torch.no_grad():
                if Cuda:
                    images = Variable(torch.from_numpy(images).cuda().type(torch.FloatTensor))
                    targets = [Variable(torch.from_numpy(ann).cuda().type(torch.FloatTensor)) for ann in targets]
                else:
                    images = Variable(torch.from_numpy(images).type(torch.FloatTensor))
                    targets = [Variable(torch.from_numpy(ann).type(torch.FloatTensor)) for ann in targets]
            # 前向传播
            out = net(images)
            # 清零梯度
            optimizer.zero_grad()
            # 计算loss
            loss_l, loss_c = criterion(out, targets)
            loss = loss_l + loss_c
            # 反向传播
            loss.backward()
            optimizer.step()
            # 加上
            loc_loss += loss_l.item()
            conf_loss += loss_c.item()

            print('\nEpoch:'+ str(epoch+1) + '/' + str(Epoch))
            print('iter:' + str(iteration) + '/' + str(epoch_size) + ' || Loc_Loss: %.4f || Conf_Loss: %.4f ||' % (loc_loss/(iteration+1),conf_loss/(iteration+1)), end=' ')

        print('Saving state, iter:', str(epoch+1))
        torch.save(model.state_dict(), 'logs/Epoch%d-Loc%.4f-Conf%.4f.pth'%((epoch+1),loc_loss/(iteration+1),conf_loss/(iteration+1)))
