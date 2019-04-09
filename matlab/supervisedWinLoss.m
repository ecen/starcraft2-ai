data = load("data/win-loss.csv")
[n, p] = size(data);
m = 800
nr=data(1:m,1);
trainLoss=data(1:m,2);
validationLoss=data(1:m,3);

scatter(nr, trainLoss, 20, validationLoss, 'filled')
scatter(nr, validationLoss, 20, trainLoss, 'filled')
colorbar