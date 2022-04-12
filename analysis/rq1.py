#!/usr/bin/env python
# coding: utf-8

from utils import save_table, load_data_csv, sns, set_style, save_figure

set_style()

df = load_data_csv("kotlin", "basic-usage.csv")

total_counts = df.groupby(['project', 'location'], as_index = False).sum()[['project', 'location', 'count']].rename(columns = {'count': 'total'})
counted = df.groupby(['project', 'location', 'isinferred'], as_index = False).sum()[['project', 'location', 'isinferred', 'count']]
summarized = counted.merge(total_counts, on=['project', 'location'], how='left')
summarized['percent'] = summarized.apply(lambda x: x.count / x.total, axis = 1)
plt.figure()
fig, ax = plt.subplots(1,1)
sns.boxplot(x='location', y='percent', hue='isinferred', data=summarized, ax = ax, legend = True)
plt.legend(['Inferred', 'Not Inferred'])
save_figure(fig, "figures/rq1-usage.pdf", 7, 4)
