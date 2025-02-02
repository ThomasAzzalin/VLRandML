import pandas as pd
from sklearn.model_selection import train_test_split

def clean_data_set(reg):
    data_set = pd.read_csv(f".\\{reg}\\data_set_unfiltered.csv")
    column_1 = "team_a_atk_win"
    column_2 = "team_a_def_win"
    filtered_data = data_set[~((data_set[column_1] == 0) & (data_set[column_2] == 0))]

    column_1 = "team_b_atk_win"
    column_2 = "team_b_def_win"
    filtered_data = filtered_data[~((filtered_data[column_1] == 0) & (filtered_data[column_2] == 0))]

    column_delete = ['url_match','date_match', 'team_a_general_win', 'team_b_general_win']
    filtered_data = filtered_data.drop(columns=column_delete)
    filtered_data.to_csv(f".\\{reg}\\data_sets\\data_set_filtered.csv", index=False)

if __name__ == '__main__':
    reg = input("Insert the region: ")
    clean_data_set(reg)
    file_path = f".\\{reg}\\data_sets\\data_set_filtered.csv"
    data = pd.read_csv(file_path)

    # Dividi il dataset in 80% training e 20% evaluation
    train_data, eval_data = train_test_split(data, test_size=0.2, random_state=42)

    # Salva i due dataset in due file CSV separati
    train_data.to_csv(f".\\{reg}\\data_sets\\training_dataset.csv", index=False)
    eval_data.to_csv(f".\\{reg}\\data_sets\\evaluation_dataset.csv", index=False)

