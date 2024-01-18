# importing python libraries
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os
import warnings

warnings.filterwarnings('ignore')

# Set a seed for reproducibility
np.random.seed(42)
random.seed(42)


def CreateData():
    try:
    # the file to contain the data is Accounting.xlsx
        xls = pd.ExcelFile("Accounting.xlsx")
        # the tables would be stored in each sheet
        workers = xls.parse('Workers')
        products = xls.parse('Products')
        transactions = xls.parse('Transactions')
        print("Data loaded from file.")
        print ()
    except FileNotFoundError:
        print("File not found. Generating dummy data...")
        # to generate the data
        num_workers = 5
        workers = pd.DataFrame({
        'WorkerID': range(1, num_workers + 1),
        'WorkerName': ['Worker{}'.format(i) for i in range(1, num_workers + 1)],
        'HourlyRate': random.choices([10, 15, 20], (15, 30, 15), k= 5)
        })

        # Generate dummy data for Products
        num_products = 10
        products = pd.DataFrame({
            'ProductID': range(1, num_products + 1),
            'ProductName': ['Product{}'.format(i) for i in range(1, num_products + 1)],
            'CostOfGoods': [random.randint(10, 30) for _ in range(num_products)]
        })

        # Generate dummy data for Transactions
        num_transactions = 300000
        transactions = pd.DataFrame({
            'TransactionID': range(1, num_transactions + 1),
            'Date': [datetime(2023, 12, 1) + timedelta(days=random.randint(0, 60)) for _ in range(num_transactions)],
            'Shift': [random.choice([1, 2]) for _ in range(num_transactions)],
            'ProductID': np.random.randint(1, num_products + 1, num_transactions),
            'QuantitySold': np.random.randint(1, 20, num_transactions),
            'UnitPrice': np.round(np.random.uniform(5, 50, num_transactions), decimals= 2),
            'WorkerID': [random.randint(1, num_workers) for _ in range(num_transactions)]
        })
        return workers, products, transactions

def JoiningData():
    workers, products, transactions = CreateData()
    merged_df = pd.merge(transactions, products, on='ProductID', how='left')
    df_accounting = pd.merge(merged_df, workers, on='WorkerID', how='left')
    df_accounting.columns = df_accounting.columns.str.replace('_x', '').str.replace('_y', '')
    return df_accounting


def CalculateSales():
    while True:
        print('To calculate Total Sales, Pick any of the following options')
        print('Press 1 to calculate today\'s Sales')
        print('Press 2 to calculate any Date Sales')
        print('Press 3 to exit')
        user_input = input()

        if user_input in ['1', '2', '3']:
            if int(user_input) == 1:
                today_date = datetime.now().date().strftime("%Y-%m-%d")
                result = df_accounting.query('Date == "{}"'.format(today_date))
                resulted = (result['UnitPrice'] * result['QuantitySold']).sum()
                print(f"The Total Sales for Today is", f"${resulted:,.2f}")
                break
            elif int(user_input) == 2:
                while True:
                    min_dt = df_accounting['Date'].min()
                    max_dt = df_accounting['Date'].max()
                    print(f"Select your date of choice between {min_dt} and {max_dt}. Use valid date using 'YYYY-MM-DD' format")
                    print("Press 0 to Exit")
                    user_input = input()
                    try:
                        if user_input == '0':
                            print("Session Ended")
                            break
                        else:
                            user_date = datetime.strptime(user_input, '%Y-%m-%d').strftime("%Y-%m-%d")
                            if min_dt <= datetime.strptime(user_date, '%Y-%m-%d').date() <= max_dt:
                                result = df_accounting.query('Date == "{}"'.format(user_date))
                                resulted = (result['CostOfGoods'] * result['QuantitySold']).sum()
                                print(f"The Total Sales for {user_input} is", f"${resulted:,.2f}")
                                break
                            else:
                                print(f"Data does not exist for {user_date}.")
                                print("...")
                                print("...")
                                continue
                    except:
                        raise Exception("Invalid Date")
                break
            else:
                print("End of session")
                break
        else:
            print("Invalid Input, try again")
            print("...")
            print("...")


def EmployeeSalary():
    while True:
        print('To calculate worker salary for the current month, please pick one of the options below')
        print('Press 1 to get salary for Worker1')
        print('Press 2 to get salary for Worker2')
        print('Press 3 to get salary for Worker3')
        print('Press 4 to get salary for Worker4')
        print('Press 5 to get salary for Worker5')
        print('Press 6 to get salary for all workers')
        print('Press 7 to Exit')
        user_input = input()

        # Validate user input
        if user_input in ['1', '2', '3', '4', '5', '6', '7']:
            if user_input == "7":
                print("Session Ended")
                break
            else:
                user_input = int(user_input)
                current_month = datetime.now().month
                distinct_combinations = df_accounting[['WorkerName', 'HourlyRate', 'Date', 'Shift']]\
                    .drop_duplicates(subset=['WorkerName', 'HourlyRate', 'Date', 'Shift'])
                distinct_combinations = distinct_combinations[distinct_combinations['Date'].dt.month == current_month]
                worker_salary = distinct_combinations.groupby(['WorkerName', 'HourlyRate'])['Shift'].count().reset_index(name='NumberOfShifts')
                worker_salary['Salary'] = (worker_salary['HourlyRate'] * worker_salary['NumberOfShifts'] * 8).map("${:,.2f}".format)
                worker_salary = worker_salary[['WorkerName', "Salary"]]

                if user_input == 6:
                    print(worker_salary)
                    break
                else:
                    specific_worker_salary = worker_salary.query(f'WorkerName == "Worker{user_input}"')
                    print(specific_worker_salary)
                    break
        else:
            print("Error: Invalid worker number. Please enter a number between 1 and 6.")
    

def SalesCostProfit():
    while True:
        print('To calculate Total Sales, Total Cost or Total Profit')
        print('Press 1 to calculate Total Sales')
        print('Press 2 to calculate Total Cost')
        print('Press 3 to calculate Total Profit')
        print('Press 4 to calculate all three')
        print('Press 5 to exit')
        user_input = input()
        
        if user_input in ['1', '2', '3', '4', '5']:
            user_input = int(user_input)
            if user_input == 5:
                print("Session Ended")
                break
            else:
                df_accounting['MonthYear'] = df_accounting['Date'].dt.to_period('M')

                # Calculate total sales, total cost, and profit
                df_accounting['Sales'] = df_accounting['QuantitySold'] * df_accounting['UnitPrice']
                df_accounting['TotalCost'] = df_accounting['CostOfGoods'] * df_accounting['QuantitySold']
                df_accounting['Profit'] = df_accounting['Sales'] - df_accounting['TotalCost']

                # Create a pivot table with a total row
                pivot_result = pd.pivot_table(df_accounting, 
                                            values=['Sales', 'TotalCost', 'Profit'],
                                            index='MonthYear',
                                            aggfunc='sum',
                                            margins=True,
                                            margins_name='Total')

                # Display the result
                pivot_result = pivot_result[['Sales', 'TotalCost', 'Profit']].applymap("${:,.2f}".format)
                if user_input == 1:
                    print()
                    print()
                    print('Results for Total Sales')
                    print(pivot_result['Sales'])
                    break
                elif user_input == 2:
                    print()
                    print()
                    print('Results for Total Cost')
                    print(pivot_result['TotalCost'])
                    break
                elif user_input == 3:
                    print()
                    print()
                    print('Results for Total Profit')
                    print(pivot_result['Profit'])
                    break
                else:
                    print()
                    print()
                    print('Results for All 3 KPIS')
                    print(pivot_result)
                    break
        else:
            print('Invalid Input, Try again')


def TotalTipForShift():
    while True:
        min_dt = df_accounting['Date'].min()
        max_dt = df_accounting['Date'].max()
        print(f"To Calculate the Total Tips from Sales for a Certain Shift, Please select a Date from {min_dt} and {max_dt}")
        print("Press 0 to Exit the session")
        user_input = input()
        try:
            if user_input == '0':
                print("Session Ended")
                print()
                print()
                break
            else:
                user_date = datetime.strptime(user_input, '%Y-%m-%d').strftime("%Y-%m-%d")
                Grouped = df_accounting.groupby(['Date', 'Shift'])["Sales"].sum()\
                    .sort_index(level=['Date', 'Shift'], ascending=[True, True])
                Grouped = Grouped.reset_index(name = "Total Sales")
                if min_dt <= datetime.strptime(user_date, '%Y-%m-%d').date() <= max_dt:
                    print("Correct Date Input, now to pick a shift")
                    while True:
                        print("Select the Shift to find Total Tips")
                        print("Press 1 for morning shift")
                        print("Press 2 for evening shift")
                        shift_input = input()
                        if shift_input == '1':
                            trunced = Grouped.query('Date == "{}" and Shift == 1'.format(user_date))
                            Total_tip = (trunced['Total Sales'].sum()) * 0.02
                            print(f"The tip sales on {user_date} during the morning shift is", f"${Total_tip:,.2f}")
                            print()
                            print()
                            break
                        elif shift_input == '2':
                            trunced = Grouped.query('Date == "{}" and Shift == 2'.format(user_date))
                            Total_tip = (trunced['Total Sales'].sum()) * 0.02
                            print(f"The tip sales on {user_date} during the morning shift is", f"${Total_tip:,.2f}")
                            print()
                            print()
                            break
                        else: 
                            print("Wrong input")
                            print()
                            print()
                            continue
                    break
                else:
                    print(f"Data does not exist for {user_date}.")
                    print()
                    print()
                    continue
        except:
            print("Wrong Data Input, Please Try Again")
            print()
            print()


def TotalDailyTip():
    while True:
        min_dt = df_accounting['Date'].min()
        max_dt = df_accounting['Date'].max()
        print(f"To Calculate the Total Tips from Sales for a Certain Day, Please select a Date from {min_dt} and {max_dt}")
        print("Press 0 to Exit the session")
        user_input = input()
        try:
            if user_input == '0':
                print("Session Ended")
                print()
                print()
                break
            else:
                user_date = datetime.strptime(user_input, '%Y-%m-%d').strftime("%Y-%m-%d")
                Grouped = df_accounting.groupby(['Date', 'Shift'])["Sales"].sum()\
                    .sort_index(level=['Date', 'Shift'], ascending=[True, True])
                Grouped = Grouped.reset_index(name = "Total Sales")
                if min_dt <= datetime.strptime(user_date, '%Y-%m-%d').date() <= max_dt:
                    trunced = Grouped.query('Date == "{}"'.format(user_date))
                    Total_tip = (trunced['Total Sales'].sum()) * 0.02
                    print(f"The Total tip on {user_date} is", f"${Total_tip:,.2f}")
                    print()
                    print()
                    break
                else:
                    print(f"Data does not exist for {user_date}.")
                    print()
                    print()
                    continue
        except:
            print("Wrong Data Input, Please Try Again")
            print()
            print()
            
df_accounting = JoiningData()

def automation():
    print("Hello There 👋, Welcome")
    print("Can I know your name please? (Alphabets only)")
    print()
    while True:
        user_name = input()
        if user_name.isalpha():
            print("Nice to have you, {}".format(user_name))
            break
        else:
            print("Enter a valid name, please (Alphabets only)")
            print()
            continue
    print()
    print()

    while True:
        print(f'What Task can I help you Automate, {user_name}? 😊')
        print()
        print('Here are the options below')
        print('Press 1 to Calculate Total Sales')
        print('Press 2 to Calculate Worker Salary')
        print('Press 3 to Calculate Monthly profit')
        print('Press 4 to Calculate Tips for a Shift')
        print('Press 5 to Calculate Total Tips for the Day')
        print('Press 6 to Exit Session')
        selected = input()
        print()

        if not (selected.isdigit() and selected in ['1', '2', '3', '4', '5', '6']):
            print("That's a wrong input. Do you want to end the session or continue?")
            print("Press 1 to continue")
            print("Press 2 to End Session")
            print()
            choice = input() 
            if choice == '1':
                continue
            elif choice == '2':
                print('Session Ended')
                break
            else:
                print("Wrong input, Session Ended")
                break
        else:
            print("You selected {}".format(selected))
            print()
            if selected == '6':
                print("Session Ended")
                break
            elif selected == '1':
                CalculateSales()
                print()
            elif selected == '2':
                EmployeeSalary()
                print()
            elif selected == '3':
                SalesCostProfit()
                print()
            elif selected == '4':
                TotalTipForShift()
                print()
            elif selected == '5':
                TotalDailyTip()
                print()
            else:
                break

        print("Do you want to end the session or continue?")
        print("Press 1 to continue")
        print("Press 2 to End Session")
        print()
        choice = input() 
        if choice == '1':
            continue
        elif choice == '2':
            print('Session Ended')
            break
        else:
            print("Wrong input, Session Ended")
            break


automation()
