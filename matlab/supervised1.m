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