#!/usr/bin/env python
# coding: utf-8

from utils import *
from matplotlib.ticker import PercentFormatter

from scipy.stats import shapiro

set_style()

summarized = load_pre_summarized('kotlin', ['project', 'location', 'isinferred'])

plt.figure()
fig, ax = plt.subplots(1,1)
sns.boxplot(x='location', y='percent', hue='isinferred', data=summarized, ax = ax, showfliers = False)
ax.yaxis.set_major_formatter(PercentFormatter(100))
ax.set_ylabel("Percent per Project")
ax.set_xlabel("")
plt.gca().legend().set_title("")
save_figure(fig, "figures/rq-usage-summary.pdf", 7, 4)

save_table(summarized[['location', 'isinferred', 'percent']].groupby(['location', 'isinferred']).describe(), "tables/rq-usage-summary.tex")

rows = []

for location in summarized['location'].unique():
    for isinferred in summarized['isinferred'].unique():
        stat, p = shapiro(summarized[(summarized['location'] == location) & (summarized['isinferred'] == isinferred)]['percent'])
        rows.append(pd.DataFrame({'Location': [location],
                                  'Inference?': [isinferred],
                                  'W': [stat],
                                  'p': [p],
                                  'Normal?': [ 'Yes' if p < 0.05 else 'No']}))

save_table(pd.concat(rows), 'tables/rq-usage-shapiro.tex')
