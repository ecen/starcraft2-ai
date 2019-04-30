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

%% Distribution comparison
data1 = load("data/dqnRepeatMin5.csv")
%data1 = load("data/dqnExploreMin-0.20.csv")
data2 = load("data/dqnRepeatMin0.csv")
[n1, p1] = size(data1);
[n2, p2] = size(data2);
m = 713
a1 = 1
a2 = 1

scores1=data1(a1:a1-1+m,1);
workers1=data1(a1:a1-1+m,4)
scores2=data2(a2:a2-1+m,1);
workers2=data2(a2:a2-1+m,4);

clf
hold on
scatter([1:m], scores1, 20, workers1, 'filled', 'MarkerEdgeColor',[0 0 0])
scatter([1:m], scores2, 20, workers2, 'd', 'filled')
hold off

colorbar;
m1 = mean(scores1)
s1 = std(scores1)
m2 = mean(scores2)
s2 = std(scores2)
clf
hold on
counts = 1
histogram(workers1(1:m), 'BinWidth', counts)
histogram(workers2(1:m), 'BinWidth', counts)
hold off

%['Fyrkantsv\aa g, $k = ', num2str(k), '$']
title('',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',12,...
    'FontName','Times')
ylabel({'number of data points'},...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
xlabel('worker units',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
legend('Original','Repeat', 'Location', 'Best');
set(gca,...
    'FontSize',10);
%ylim([-1.5 1.5])

name = ['figures/', 'dqnHistogram1', '.eps'];
print('-depsc2', name);

%% Distribution comparison
data1 = load("data/dqnWorkerRewardSupplyLocationExpdecay5-9.csv")
%data1 = load("data/dqnExploreMin-0.20.csv")
data2 = load("data/dqnRepeat3Min5.csv")
[n1, p1] = size(data1);
[n2, p2] = size(data2);
m = 700
a1 = 800
a2 = 800

scores1=data1(a1:a1-1+m,1);
workers1=data1(a1:a1-1+m,4)
scores2=data2(a2:a2-1+m,1);
workers2=data2(a2:a2-1+m,4);

clf
hold on
scatter([1:m], scores1, 20, workers1, 'filled', 'MarkerEdgeColor',[0 0 0])
scatter([1:m], scores2, 20, workers2, 'd', 'filled')
hold off

colorbar;
m1 = mean(scores1)
s1 = std(scores1)
m2 = mean(scores2)
s2 = std(scores2)
clf
hold on
counts = 1
line1 = histogram(workers1(1:m), 'BinWidth', counts)
line2 = histogram(workers2(1:m), 'BinWidth', counts)
line3 = histogram([-1000], 'BinWidth', counts)
hold off

%['Fyrkantsv\aa g, $k = ', num2str(k), '$']
title('',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',12,...
    'FontName','Times')
ylabel({'number of data points'},...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
xlabel('worker units',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
%set(line1, 'FaceColor', 'r')
%set(line2, 'FaceColor', 'g')
set(line3, 'FaceColor', [0.3 0.1 0.1]);
hL = legend([line1,line2,line3],{'Original','Repeat','(Both)'}, 'Location', 'Best');
%legend('Original','Repeat', 'Both', 'Location', 'Best');
set(gca,...
    'FontSize',10);
%ylim([-1.5 1.5])
xlim([10 35])

name = ['figures/', 'dqnHistogram1', '.eps'];
print('-depsc2', name);