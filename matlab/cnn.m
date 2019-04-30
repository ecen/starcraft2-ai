%% CNN 1 (cpu trained, ecen's laptop)

data = load("data/cnn1.csv")
[n, p] = size(data);
m = n
scores=data(1:m,1);
supply=data(1:m,4);
steps=data(1:m,3);
explorationDecay=0.9999;

clf
scatter([1:m], scores, 20, supply, 'filled');
hold on
yyaxis right
plot([1:m], max(1*explorationDecay.^steps, 0.05) * 100, 'Color', 	[0, 0.4470, 0.7410]);
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
    'FontSize',18,...
    'FontName','Times')
xlabel('episode',...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
ylabel(c, 'workers');
yyaxis right
ylabel({'exploration rate'},...
    'FontUnits','points',...
    'interpreter','latex',...
    'FontWeight','normal',...
    'FontSize',18,...
    'FontName','Times')
ytickformat('percentage');
yyaxis left
set(gca,...
    'FontSize',10);
%line([713 713], [500 5000], 'LineStyle','--', 'Color', 	[0, 0.4470, 0.7410])
legend('Network score', 'Exploration rate = 5%', 'Exploration rate', ...
    'Location', 'Best');
%xlim([0 710])

name = ['figures/', 'cnn1', '.eps'];
print('-depsc2', name);
print('BarPlot', '-dpng');

%clf
m1 = mean(scores)
s1 = std(scores)
hold on
%histogram(scores(1000:1400), 'BinWidth', 200)
%histogram(scores(300:700), 'BinWidth', 200)
hold off