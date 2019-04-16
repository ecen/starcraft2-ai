data = load("data/marine1.csv")
[n, p] = size(data);
m = n
scores=data(1:m,1);
steps=data(1:m,3);
supplyWorkers=data(1:m,4);
supplyArmy=data(1:m,5);
totalUnits=data(1:m,6);
totalUnitsKilled=data(1:m,7);
totalStructuresKilled=data(1:m,8);

gameLength=[steps(1) diff(steps.')]

explorationDecay=0.99999;

clf
scatter([1:m], totalUnits, 20, supplyWorkers, 'filled');
hold on
yyaxis right
plot([1:m], max(1*explorationDecay.^steps, 0.10));
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

name = ['figures/', 'marine1', '.eps'];
print('-depsc2', name);
%print('BarPlot', '-dpng');

%clf
m1 = mean(scores)
s1 = std(scores)
hold on
%histogram(scores(1000:1400), 'BinWidth', 200)
%histogram(scores(300:700), 'BinWidth', 200)
hold off

%% Marine2. 
% 0.999995 exploration decay

data = load("data/marine2.csv")
[n, p] = size(data);
m = n
scores=data(1:m,1);
steps=data(1:m,3);
supplyWorkers=data(1:m,4);
supplyArmy=data(1:m,5);
totalUnits=data(1:m,6);
totalUnitsKilled=data(1:m,7);
totalStructuresKilled=data(1:m,8);

gameLength=[steps(1) diff(steps.')].*12./(1000*60)

explorationDecay=0.999995;

clf
scatter([1:m], totalUnits, 20, supplyWorkers, 'filled');
hold on
yyaxis right
plot([1:m], max(1*explorationDecay.^steps, 0.10));
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

name = ['figures/', 'marine1', '.eps'];
print('-depsc2', name);
%print('BarPlot', '-dpng');

%clf
m1 = mean(scores)
s1 = std(scores)
hold on
%histogram(scores(1000:1400), 'BinWidth', 200)
%histogram(scores(300:700), 'BinWidth', 200)
hold off