    df.loc[(df['bid_volume_1']>15) & (df['ask_volume_1']>15) & (df['product']=='BANANAS'),'imbalance_status'] = 10 # high liquidity on both sides
    df.loc[(df['bid_volume_1']<=15) & (df['ask_volume_1']>15) & (df['product']=='BANANAS'),'imbalance_status'] = -1 # low liquidity on the bid side, tend to have a negative price movement
    df.loc[(df['bid_volume_1']>15) & (df['ask_volume_1']<=15) & (df['product']=='BANANAS'),'imbalance_status'] = 1 # low liquidity on the ask side, tend to have a positive price movement
    df.loc[(df['bid_volume_1']<=15) & (df['ask_volume_1']<=15) & (df['product']=='BANANAS'),'imbalance_status'] = 0 # low liquidity on both sides

    df.loc[(df['bid_volume_1']>15) & (df['ask_volume_1']>15) & (df['product']=='PEARLS'),'imbalance_status'] = 10
    df.loc[(df['bid_volume_1']<=15) & (df['ask_volume_1']>15) & (df['product']=='PEARLS'),'imbalance_status'] = -1
    df.loc[(df['bid_volume_1']>15) & (df['ask_volume_1']<=15) & (df['product']=='PEARLS'),'imbalance_status'] = 1
    df.loc[(df['bid_volume_1']<=15) & (df['ask_volume_1']<=15) & (df['product']=='PEARLS'),'imbalance_status'] = 0

    df.loc[(df['bid_volume_1']>10) & (df['ask_volume_1']>10) & (df['product']=='DIVING_GEAR'),'imbalance_status'] = 10
    df.loc[(df['bid_volume_1']<=10) & (df['ask_volume_1']>10) & (df['product']=='DIVING_GEAR'),'imbalance_status'] = -1
    df.loc[(df['bid_volume_1']>10) & (df['ask_volume_1']<=10) & (df['product']=='DIVING_GEAR'),'imbalance_status'] = 1
    df.loc[(df['bid_volume_1']<=10) & (df['ask_volume_1']<=10) & (df['product']=='DIVING_GEAR'),'imbalance_status'] = 0

    df.loc[(df['bid_volume_1']>40) & (df['ask_volume_1']>40) & (df['product']=='BERRIES'),'imbalance_status'] = 10
    df.loc[(df['bid_volume_1']<=40) & (df['ask_volume_1']>40) & (df['product']=='BERRIES'),'imbalance_status'] = -1
    df.loc[(df['bid_volume_1']>40) & (df['ask_volume_1']<=40) & (df['product']=='BERRIES'),'imbalance_status'] = 1
    df.loc[(df['bid_volume_1']<=40) & (df['ask_volume_1']<=40) & (df['product']=='BERRIES'),'imbalance_status'] = 0