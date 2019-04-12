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
data = load("data/dqnWorkerRewardSupply2.csv")
[n, p] = size(data);
scores=data(1:n,1);
supply=data(1:n,4);
steps=data(1:n,3);
explorationDecay=0.9999

clf
scatter([1:n], scores, 20, supply, 'filled')
hold on
yyaxis right
plot([1:n], max(1*explorationDecay.^steps, 0.05));
hold off
c = colorbar;
yyaxis left

title('',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',12,...
    'FontName','Times')
ylabel({'score'},...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...z
    'FontName','Times')
xlabel('episode',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
ylabel(c, 'workers');
set(gca,...
    'FontSize',10);
%ylim([-1.5 1.5])

name = ['figures/', 'dqnWorkerRewardSupply', '.eps'];
print('-depsc2', name);

%% Continous worker rewards, with pre-determined supply depot locations
data = load("data/dqnWorkerRewardSupplyLocations.csv")
[n, p] = size(data);
m = n
scores=data(1:m,1);
supply=data(1:m,4);
steps=data(1:m,3);
explorationDecay=0.9999;

clf
scatter([1:m], scores, 20, supply, 'filled')
hold on
yyaxis right
plot([1:m], max(1*explorationDecay.^steps, 0.05));
hold off
c = colorbar;
yyaxis left

title('',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',12,...
    'FontName','Times')
ylabel({'score'},...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...z
    'FontName','Times')
xlabel('episode',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
ylabel(c, 'workers');
set(gca,...
    'FontSize',10);
%ylim([-1.5 1.5])

name = ['figures/', 'dqnWorkerRewardSupplyLocation', '.eps'];
print('-depsc2', name);

%% Random action
data = load("data/dqnRandom.csv")
[n, p] = size(data);
m = 800
scores=data(1:m,1);
supply=data(1:m,4);

scatter([1:m], scores, 20, supply, 'filled')
c = colorbar

title('',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',12,...
    'FontName','Times')
ylabel({'score'},...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
xlabel('episode',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
ylabel(c, 'workers');
set(gca,...
    'FontSize',10);
%ylim([-1.5 1.5])

name = ['figures/', 'dqnRandom', '.eps'];
print('-depsc2', name);

%% Random vs Continous worker reward pre-determined supply
data1 = load("data/dqnRandom.csv")
data2 = load("data/dqnWorkerRewardSupplyLocationExpdecay5-9.csv")
[n1, p1] = size(data1);
[n2, p2] = size(data2);
m = min(n1, n2);

scores1=data1(1:m,1);
workers1=data1(1:m,4)
scores2=data2(1:m,1);
workers2=data2(1:m,4);

clf
hold on
scatter([1:m], scores1, 20, 'filled', 'MarkerFaceColor', [0 0.4470 0.7410])
scatter([1:m], scores2, 20, 'filled', 'MarkerFaceColor', [0.9290 0.6940 0.1250])
hold off
m1 = mean(scores1)
s1 = std(scores1)
m2 = mean(scores2)
s2 = std(scores2)
%histogram(scores1(300:m))
%histogram(scores2(300:m))

%['Fyrkantsv\aa g, $k = ', num2str(k), '$']
title('',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',12,...
    'FontName','Times')
ylabel({'score'},...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
xlabel('episode',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
legend('Random','Trained');
set(gca,...
    'FontSize',10);
%ylim([-1.5 1.5])

name = ['figures/', 'randomVsWorkerRewardPreDetermined', '.eps'];
print('-depsc2', name);

%% Continous worker rewards, random supply depots, 5 nines 
data = load("data/dqnWorkerRewardExpdecay5-9.csv")
[n, p] = size(data);
m = n
scores=data(1:m,1);
supply=data(1:m,4);
steps=data(1:m,3);
explorationDecay=0.99999;

clf
scatter([1:m], scores, 20, supply, 'filled')
hold on
yyaxis right
plot([1:m], max(1*explorationDecay.^steps, 0.05));
hold off
c = colorbar;
yyaxis left

title('',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',12,...
    'FontName','Times')
ylabel({'score'},...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...z
    'FontName','Times')
xlabel('episode',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
ylabel(c, 'workers');
set(gca,...
    'FontSize',10);
%ylim([-1.5 1.5])

name = ['figures/', 'dqnWorkerRewardExpdecay5-9', '.eps'];
print('-depsc2', name);



%% Continous worker rewards, better pre-determined supply depots, 5 nines 
data = load("data/dqnWorkerRewardSupplyLocationExpdecay5-9.csv")
[n, p] = size(data);
m = 1000
scores=data(1:m,1);
supply=data(1:m,4);
steps=data(1:m,3);
explorationDecay=0.99999;

clf
scatter([1:m], scores, 20, supply, 'filled');
hold on
yyaxis right
plot([1:m], max(1*explorationDecay.^steps, 0.05));
yyaxis left
stepSize=100
means = []
deviations = []
j = 1
for i=1:stepSize:m-stepSize
    i
    means(j)=mean(scores(i:i+stepSize));
    deviations(j)=std(scores(i:i+stepSize));
    j = j + 1;
end
means;
deviations;
eb = errorbar([1:stepSize:m-stepSize] + stepSize/2, means, deviations * 2)
eb.Color = 'black';
eb.CapSize = stepSize/4;
hold off
c = colorbar;
%yyaxis left

title('',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',12,...
    'FontName','Times')
ylabel({'score'},...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...z
    'FontName','Times')
xlabel('episode',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
ylabel(c, 'workers');
set(gca,...
    'FontSize',10);
%xlim([0 710])

name = ['figures/', 'dqnWorkerRewardExpdecay5-9', '.eps'];
print('-depsc2', name);
print('BarPlot', '-dpng');

%clf
m1 = mean(scores)
s1 = std(scores)
hold on
%histogram(scores(1000:1400), 'BinWidth', 200)
%histogram(scores(300:700), 'BinWidth', 200)
hold off

%% Continous worker rewards, 
% better pre-determined supply depots, 5 nines Test

data = load("data/dqnWorkerRewardSupplyLocationExpdecay5-9Test.csv")
[n, p] = size(data);
m = n
scores=data(1:m,1);
supply=data(1:m,4);
steps=data(1:m,3);
explorationDecay=0.99999;

clf
scatter([1:m], scores, 20, supply, 'filled');
hold on
yyaxis right
plot([1:m], max(1*explorationDecay.^steps, 0.05));
yyaxis left
stepSize=100
means = []
deviations = []
j = 1
for i=1:stepSize:m-stepSize
    i
    means(j)=mean(scores(i:i+stepSize));
    deviations(j)=std(scores(i:i+stepSize));
    j = j + 1;
end
means;
deviations;
%eb = errorbar([1:stepSize:m-stepSize] + stepSize/2, means, deviations * 2)
%eb.Color = 'black';
%eb.CapSize = stepSize/4;
hold off
c = colorbar;
%yyaxis left

title('',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',12,...
    'FontName','Times')
ylabel({'score'},...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...z
    'FontName','Times')
xlabel('episode',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
ylabel(c, 'workers');
set(gca,...
    'FontSize',10);
%xlim([0 710])

name = ['figures/', 'dqnWorkerRewardExpdecay5-9', '.eps'];
%print('-depsc2', name);
%print('BarPlot', '-dpng');

m1 = mean(scores)
s1 = std(scores)
%histogram(scores(1:m))

%% Explore value tests
data1 = load("data/dqnTestExplore-0.05.csv")
data2 = load("data/dqnTestExplore-0.00.csv")
[n1, p1] = size(data1);
[n2, p2] = size(data2);
m = min(n1, n2);

scores1=data1(1:m,1);
workers1=data1(1:m,4)
scores2=data2(1:m,1);
workers2=data2(1:m,4);

clf
hold on
scatter([1:m], scores1, 20, workers1, 'filled', 'MarkerEdgeColor',[0 0 0])
scatter([1:m], scores2, 20, workers2, 'd', 'filled')
hold off
clf
colorbar;
m1 = mean(scores1)
s1 = std(scores1)
m2 = mean(scores2)
s2 = std(scores2)
hold on
counts = 200
histogram(scores1(1:m), 'BinWidth', counts)
histogram(scores2(1:m), 'BinWidth', counts)
hold off

%['Fyrkantsv\aa g, $k = ', num2str(k), '$']
title('',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',12,...
    'FontName','Times')
ylabel({'score'},...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
xlabel('episode',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
legend('0.05','0.00');
set(gca,...
    'FontSize',10);
%ylim([-1.5 1.5])

name = ['figures/', 'randomVsWorkerRewardPreDetermined', '.eps'];
print('-depsc2', name);

%% Continous worker rewards, better pre-determined supply depots, 5 nines 
data = load("data/dqnExploreMin-0.20.csv")
[n, p] = size(data);
m = n
scores=data(1:m,1);
supply=data(1:m,4);
steps=data(1:m,3);
explorationDecay=0.99999;

clf
scatter([1:m], scores, 20, supply, 'filled');
hold on
yyaxis right
plot([1:m], max(1*explorationDecay.^steps, 0.20));
yyaxis left
stepSize=100
means = []
deviations = []
j = 1
for i=1:stepSize:m-stepSize
    i
    means(j)=mean(scores(i:i+stepSize));
    deviations(j)=std(scores(i:i+stepSize));
    j = j + 1;
end
means;
deviations;
%eb = errorbar([1:stepSize:m-stepSize] + stepSize/2, means, deviations * 2)
%eb.Color = 'black';
%eb.CapSize = stepSize/4;
hold off
c = colorbar;
%yyaxis left

title('',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',12,...
    'FontName','Times')
ylabel({'score'},...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...z
    'FontName','Times')
xlabel('episode',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
ylabel(c, 'workers');
set(gca,...
    'FontSize',10);
%xlim([0 710])

name = ['figures/', 'dqnExploreMin-0.20', '.eps'];
print('-depsc2', name);
%print('BarPlot', '-dpng');

%clf
m1 = mean(scores)
s1 = std(scores)
hold on
%histogram(scores(1000:1400), 'BinWidth', 200)
%histogram(scores(300:700), 'BinWidth', 200)
hold off
