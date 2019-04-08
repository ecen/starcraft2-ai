%% Continous reward: workers
data = load("data/dqnWorkerReward.csv");
[n, p] = size(data);
scores=data(1:800,1);
%time=dqnWorkerReward(1:n,2)
plot([1:800], scores, '.');
lsline;

%% Sparse reward: total mineral count
data = load("data/dqnSparse.csv");
[n, p] = size(data);
scores=data(1:n,1);
%time=dqnSparse(1:n,2)
plot([1:n], scores, '.');
lsline;

%% Continous reward: total mineral count

data = load("data/dqnTotalMineral.csv")
[n, p] = size(data)
scores=data(1:n,1)
%time=dqnTotalMineral(1:n,2)
plot([1:n], scores, '.')
lsline

%% Naive Boltzmann, sparse reward, total mineral count

data = load("data/dqnBoltzmannNaiveSparse.csv")
[n, p] = size(data);
scores=data(1:n,1);
%time=dqnBoltzmannNaiveSparse(1:n,2)
plot([1:n], scores, '.');
lsline;

%% Naive Boltzmann, continous reward

data = load("data/dqnBoltzmannNaive.csv");
[n, p] = size(data);
scores=data(1:n,1);
plot([1:n], scores, '.');
lsline;

%% Naive Boltzmann, continous reward, linear output layer

data = load("data/dqnBoltzmannNaiveLinear.csv")
[n, p] = size(data);
scores=data(1:n,1);
plot([1:n], scores, '.');
lsline;

%% Continous worker rewards, with supplies in data
data = load("data/dqnWorkerRewardSupply.csv")
[n, p] = size(data);
scores=data(1:n,1);
supply=data(1:n,4);

scatter([1:n], scores, 20, supply, 'filled')
colorbar

lsline;

%% Continous worker rewards, with pre-determined supply depot locations
data = load("data/dqnWorkerRewardSupplyLocations.csv")
[n, p] = size(data);
m = n
scores=data(1:m,1);
supply=data(1:m,4);

scatter([1:m], scores, 20, supply, 'filled')
colorbar

%% Random action
data = load("data/dqnRandom.csv")
[n, p] = size(data);
m = n
scores=data(1:m,1);
supply=data(1:m,4);

scatter([1:m], scores, 20, supply, 'filled')
colorbar