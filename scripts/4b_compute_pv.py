import pandas as pd
import module_global
import config


def compute_pv(df_loaded):
    
    computed_situation = df_loaded.copy()
    computed_situation['PTA'] = float(0)
    computed_situation['PTA_fees_not_integrated'] = float(0)
    computed_situation['plus_value'] = float(0)
    computed_situation['plus_value_fees_not_integrated'] = float(0)
    computed_situation['fraction_capital_initial'] = float(0)

    print("Plus ou moins-value brute = Prix de cession – [Prix total d'acquisition x Prix de cession / Valeur globale du portefeuille]")
    for row_index in range(1,len(df_loaded)) : 
        money_movement = computed_situation.loc[row_index, 'Money_movement']
        wallet_value_eur = computed_situation.loc[row_index, 'wallet_value_eur']
        fee_net_worth = computed_situation.loc[row_index, 'Fee Net Worth']

        if computed_situation.loc[row_index, 'Money_movement'] > 0 and computed_situation.loc[row_index, 'Detected Type'] == 'buy' :
            print("buy so PTA")
            computed_situation.loc[row_index, 'wallet_value_eur_m1'] = wallet_value_eur - money_movement
            computed_situation.loc[row_index, 'PTA'] = computed_situation.loc[row_index-1, 'PTA'] + money_movement + fee_net_worth
            computed_situation.loc[row_index, 'PTA_fees_not_integrated'] = computed_situation.loc[row_index-1, 'PTA_fees_not_integrated'] + money_movement  
        
        elif computed_situation.loc[row_index, 'Money_movement'] > 0 and computed_situation.loc[row_index, 'Detected Type'] == 'sell' :
            print("sell so PTA")
            prix_cession = money_movement
            wallet_value_eur_m1 = wallet_value_eur + money_movement
            computed_situation.loc[row_index, 'wallet_value_eur_m1'] = wallet_value_eur_m1
  
            fraction_capital_initial = (computed_situation.loc[row_index - 1, 'PTA'] * prix_cession / wallet_value_eur_m1)
            fraction_capital_initial_fees_not_integrated = (computed_situation.loc[row_index - 1, 'PTA_fees_not_integrated'] * prix_cession / wallet_value_eur_m1)
            plus_value = prix_cession - fraction_capital_initial 
            plus_value_fees_not_integrated = prix_cession - fraction_capital_initial_fees_not_integrated 
            
            computed_situation.loc[row_index, 'PTA'] = computed_situation.loc[row_index - 1, 'PTA'] - fraction_capital_initial + computed_situation.loc[row_index, 'Fee Net Worth']
            computed_situation.loc[row_index, 'PTA_fees_not_integrated'] = computed_situation.loc[row_index - 1, 'PTA_fees_not_integrated'] - fraction_capital_initial
            computed_situation.loc[row_index, 'fraction_capital_initial'] = fraction_capital_initial
            computed_situation.loc[row_index, 'plus_value'] = plus_value
            computed_situation.loc[row_index, 'plus_value_fees_not_integrated'] = plus_value_fees_not_integrated
        else :
            print("nor sell nor buy")
            computed_situation.loc[row_index, 'PTA'] = computed_situation.loc[row_index-1, 'PTA']
            computed_situation.loc[row_index, 'PTA_fees_not_integrated'] = computed_situation.loc[row_index-1, 'PTA_fees_not_integrated']


    return computed_situation



    

# File path
computed_situation_path = config.FILE_COMPUTED_PV
enriched_situation_path = config.FILE_CRYPTO_POSITIONS

enriched_situation = pd.read_csv(enriched_situation_path, sep=',')
computed_pv = compute_pv(enriched_situation.copy(deep=True))


# Pv = Prix de cession – (Prix total d'acquisition x Prix de cession / Valeur globale du portefeuille)
computed_pv.to_csv(computed_situation_path, index=False)
