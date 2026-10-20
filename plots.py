"""Scientific figures; numeric annotations read from computed result tables."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from matplotlib.animation import FuncAnimation, PillowWriter

P=Path(__file__).resolve().parent
F=P/'results/figures'; F.mkdir(exist_ok=True)
BG='#080F1A'; PANEL='#101D2E'; GRID='#24344A'; TEXT='#F1F5FF'; MUTED='#A4B5CC'
MINT='#2DDDC5'; CORAL='#FF617D'; AMBER='#F4C465'; BLUE='#76A9FF'
plt.rcParams.update({'figure.facecolor':BG,'axes.facecolor':PANEL,'text.color':TEXT,
    'axes.labelcolor':MUTED,'xtick.color':MUTED,'ytick.color':MUTED,
    'axes.edgecolor':GRID,'grid.color':GRID,'font.family':'DejaVu Sans','font.size':13,
    'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':BG})
stats=pd.read_csv(P/'results/statistics.csv')
primary=stats.query("period == 'evaluation_2000_2025' and horizon == 21 and hac_lag == 63").set_index('factor')
order=['Mkt-RF','SMB','HML','Mom']
names=['Market excess','Size (SMB)','Value (HML)','Momentum']

def base(k,title,subtitle):
    fig=plt.figure(figsize=(10.8,13.5),dpi=100)
    fig.text(.075,.955,f'OVERLAP EVIDENCE LAB   /   {k:02d}',color=MINT,fontsize=12,weight='bold')
    fig.text(.075,.904,title,fontsize=29,weight='bold',va='top',linespacing=1.2)
    fig.text(.075,.80,subtitle,fontsize=14,color=MUTED,va='top',linespacing=1.5)
    return fig

def footer(fig,text):
    fig.text(.075,.067,text,fontsize=11,color=MUTED,va='bottom',linespacing=1.5)
    fig.text(.075,.025,'GUILLEM NAVARRA   •   Kenneth French daily factors   •   2000–2025',fontsize=10,color=MUTED)

fig=base(1,'Same returns.\nMuch less evidence.',
    f'{int(primary.n_windows.iloc[0]):,} overlapping 21-session P&L windows.\nOnly the standard error changes. The average stays fixed.')
ax=fig.add_axes([.235,.31,.66,.40])
for i,(factor,name) in enumerate(zip(order,names)):
    r=primary.loc[factor]
    ax.plot([r.t_hac,r.t_iid],[i,i],color=GRID,lw=7,zorder=1)
    ax.scatter(r.t_iid,i,s=150,color=CORAL,zorder=3)
    ax.scatter(r.t_hac,i,s=150,color=MINT,zorder=3)
    ax.text(r.t_iid+.25,i+.12,f'{r.t_iid:.2f}',color=CORAL,fontsize=14,weight='bold')
    ax.text(r.t_hac,i-.21,f'{r.t_hac:.2f}',color=MINT,fontsize=14,weight='bold',ha='center')
ax.set(yticks=range(4),yticklabels=names,xlim=(-.2,12.7),ylim=(-.55,3.6),xlabel='t-statistic for mean P&L = 0')
ax.invert_yaxis(); ax.grid(axis='x',alpha=.5)
ax.axvline(1.96,color=AMBER,ls='--',lw=1.4)
ax.text(2.15,3.45,'1.96 reference',color=AMBER,fontsize=11)
fig.text(.075,.245,'●  Treat every window as independent',color=CORAL,fontsize=15)
fig.text(.075,.213,'●  Account for dependence: Newey–West, 63 lags',color=MINT,fontsize=15)
r=primary.loc['Mom']
fig.text(.075,.145,f'Momentum: t = {r.t_iid:.2f} becomes {r.t_hac:.2f}.',fontsize=23,weight='bold')
footer(fig,'Arithmetic factor P&L, not compounded returns or a tradable backtest.\nAsymptotic inference; four descriptive tests, no multiplicity adjustment.')
fig.savefig(F/'01_same_returns_less_evidence.png'); plt.close(fig)

fig=base(2,'The mean didn’t move.\nThe interval did.',
    'Mean 21-session factor P&L and approximate 95% intervals.\nBoth methods use exactly the same observations.')
ax=fig.add_axes([.235,.32,.66,.39])
for i,(factor,name) in enumerate(zip(order,names)):
    r=primary.loc[factor]
    ax.errorbar(r['mean'],i-.11,xerr=1.96*r.se_iid,fmt='o',color=CORAL,capsize=5,lw=3,ms=7)
    ax.errorbar(r['mean'],i+.11,xerr=1.96*r.se_hac,fmt='o',color=MINT,capsize=5,lw=3,ms=7)
ax.set(yticks=range(4),yticklabels=names,ylim=(-.6,3.6),xlabel='Arithmetic P&L over 21 sessions')
ax.xaxis.set_major_formatter(PercentFormatter(1,decimals=1)); ax.invert_yaxis()
ax.axvline(0,color=AMBER,ls='--',lw=1.5); ax.grid(axis='x',alpha=.5)
fig.text(.075,.26,'●  Independent-window interval',color=CORAL,fontsize=15)
fig.text(.075,.229,'●  Dependence-aware interval (63 lags)',color=MINT,fontsize=15)
fig.text(.075,.156,f'Momentum mean: {r["mean"]:.2%}\nDependence-aware interval: {r["mean"]-1.96*r.se_hac:.2%} to {r["mean"]+1.96*r.se_hac:.2%}',fontsize=20,weight='bold',linespacing=1.5)
footer(fig,'Intervals are mean ± 1.96 SE, not a guarantee of 95% finite-sample coverage.\nCurrent revised factor data; no costs or future-profitability claim.')
fig.savefig(F/'02_intervals.png'); plt.close(fig)

fig=base(3,'Longer labels can\nmagnify false precision.',
    'How much larger is the dependence-aware standard error?\nMore shared days usually means more reused information.')
ax=fig.add_axes([.13,.32,.77,.40])
colors=[BLUE,MINT,AMBER,CORAL]
for factor,name,color in zip(order,names,colors):
    s=stats.query("period == 'evaluation_2000_2025' and hac_lag == 3*horizon and factor == @factor").sort_values('horizon')
    ax.plot(s.horizon,s.se_ratio,'o-',lw=2.5,ms=6,color=color,label=name)
h=np.arange(1,64)
ax.plot(h,np.sqrt(h),ls='--',color=MUTED,lw=1.6,label='√h: iid daily reference')
ax.set(xlabel='Window length h (trading sessions)',ylabel='SE with dependence / naive SE',xlim=(0,65),ylim=(0,9))
ax.set_xticks([1,5,10,21,42,63]); ax.grid(alpha=.45)
ax.legend(loc='upper left',fontsize=11,facecolor=PANEL,edgecolor=GRID,labelcolor=TEXT)
ax.axvline(21,color=MUTED,lw=1,ls=':')
fig.text(.075,.237,f'At 21 sessions: {primary.se_ratio.min():.2f}× to {primary.se_ratio.max():.2f}× larger SE.',fontsize=22,weight='bold')
fig.text(.075,.169,'Adjacent 21-session windows share 20 daily returns.\nCount the dependence before trusting the t-statistic.',fontsize=18,linespacing=1.6)
footer(fig,'Bartlett/Newey–West bandwidth = 3h. Dashed line is a theoretical reference,\nnot an estimated confidence bound. Bandwidth and nonstationarity matter.')
fig.savefig(F/'03_horizon_sensitivity.png'); plt.close(fig)

# Motion explains the mechanical overlap using one fixed observed date segment.
daily=pd.read_csv(P/'data/daily_factors.csv',index_col=0,parse_dates=True).loc['2020-01-01':].iloc[:63]
fig=plt.figure(figsize=(10.8,13.5),dpi=80)
fig.text(.075,.93,'ONE NEW DAY.\nTWENTY REUSED.',fontsize=29,weight='bold',va='top')
fig.text(.075,.80,'Sliding 21-session momentum P&L windows\nObserved daily factor returns, early 2020',color=MUTED,fontsize=15,linespacing=1.6)
ax=fig.add_axes([.12,.29,.78,.41])
bars=ax.bar(np.arange(63),daily.Mom.to_numpy()*100,color=GRID,width=.8)
ax.set(xlim=(-1,64),ylabel='Daily momentum return (%)',xlabel='Trading session in fixed 2020 segment')
ax.grid(axis='y',alpha=.4)
label=fig.text(.075,.18,'',fontsize=19,linespacing=1.6)
fig.text(.075,.06,'Arithmetic sum, constant notional. Mint = current window.\nCoral = the one newly added daily return. No simulated executions.',color=MUTED,fontsize=12,linespacing=1.5)
def update(i):
    for j,b in enumerate(bars):
        b.set_color(CORAL if j==i+20 else MINT if i<=j<i+20 else GRID)
    total=daily.Mom.iloc[i:i+21].sum()
    label.set_text(f'{daily.index[i]:%d %b} to {daily.index[i+20]:%d %b %Y}\n21-session sum: {total:+.2%}')
    return list(bars)+[label]
anim=FuncAnimation(fig,update,frames=43,interval=180,blit=False)
anim.save(F/'overlap_window.gif',writer=PillowWriter(fps=5))
for i in [0,20,42]:
    update(i); fig.savefig(F/f'animation_frame_{i:02d}.png')
plt.close(fig)
print('Saved three publication PNGs, GIF, and three QA frames.')
