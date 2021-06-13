import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import matplotlib as plt
import plotly.figure_factory as ff
from bokeh.plotting import figure
import plotly.express as px
import zipfile


# Security
#passlib,hashlib,bcrypt,scrypt
import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False
# DB Management
import sqlite3
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data



def main():
	"""Analysis Presentation"""

	st.title("Analysis Presentation")

	menu = ["Home","Login","SignUp"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Home":
		st.subheader("Home")

	elif choice == "Login":
		st.subheader("Login Section")

		username = st.sidebar.text_input("User Name")
		password = st.sidebar.text_input("Password",type='password')
		if st.sidebar.checkbox("Login"):
			# if password == '12345':
			create_usertable()
			hashed_pswd = make_hashes(password)

			result = login_user(username,check_hashes(password,hashed_pswd))
			if result:

				st.success("Logged In as {}".format(username))

				task = st.selectbox("Task",["Add Post","Analytics","Profiles"])
				if task == "Add Post":
					st.subheader("Add Your Post")

				elif task == "Analytics":
					st.subheader("Analytics")
					# Display text in title formatting.
					st.title('Product Distribution Since 2019')
					# Display text in subheader formatting.
					st.subheader('Introduction')
					# Display string formatted as Markdown.
					st.markdown('''Starting from 2019 January six of the seven hubs in Bidhaa Sasa were fully functional with at least five working GCs. This analysis tries to compare performance across these hubs mainly concentrating on:
					* General Product Distribution per hub, product and Gender
					* Fringe Product Uptake per hub and product
					* TRP Distribution per hub, product, gender and across installments
					* Write Distribution per hub, product and Gender
					''')

					# example 2
					ldatecols = ['Date Of Birth', 'Submitted On Date', 'Approved On Date', 'Disbursed On Date',
								 'Expected Firstrepayment On Date', 'Expected Matured On Date', 'Matured On Date',
								 'Closed On Date', 'Writtenoff On Date']
					with zipfile.ZipFile('D:\Downloads\Loans1_20161227110112.zip') as z:
						with z.open("Loans1_20161227110112.csv") as f:
							loans = pd.read_csv(f, sep=';', parse_dates=ldatecols)
					loans.columns = [c.replace(' ', '_') for c in loans.columns]
					approved_loans = loans[loans.Approved_On_Date.ge('2015-01-01')]
					approved_loans['Year'] = approved_loans['Approved_On_Date'].dt.year
					approved_loans['Month'] = approved_loans['Approved_On_Date'].dt.month
					branch_counts = approved_loans.groupby('Branch_Name')[
						'Client_Id'].count().to_frame().reset_index().rename(columns={'Client_Id': 'Count'})
					product_counts = approved_loans.groupby('Product_Name')[
						'Client_Id'].count().to_frame().reset_index().rename(columns={'Client_Id': 'Count'})

					fig1 = px.bar(branch_counts, x="Branch_Name", y='Count', color='Branch_Name', text='Count',
								  width=900, height=600)
					fig1.update_traces(texttemplate='%{text:.2s}', textposition='outside')
					fig1.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', showlegend=False)

					fig2 = px.bar(product_counts, x="Product_Name", y='Count', color='Product_Name', text='Count',
								  width=1200, height=700)
					fig2.update_traces(texttemplate='%{text:.2s}', textposition='outside')
					fig2.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', showlegend=False)

					st.write(fig1)
					st.write(fig2)
					# reading disbursed loans
					with zipfile.ZipFile('D:\Downloads\Disbursed Loans Report-28-04-2021.zip') as z:
						with z.open("Disbursed Loans Report-28-04-2021.csv") as f:
							disbursedloans = pd.read_csv(f, parse_dates=['Disbursed'], skiprows=13,
														 dtype={' Disbursed': np.datetime64})
					disbursedloans.dropna(axis=0, inplace=True, subset=['Client name', 'DOB', 'ID Card', 'Gender'])
					disbursedloans = disbursedloans.loc[:, ~disbursedloans.columns.str.contains('^Unnamed')]
					disbursedloans['TRP'] = disbursedloans['TRP'].str.rstrip('%').astype('float')
					disbursedloans['Year'] = disbursedloans['Disbursed'].dt.year
					disbursedloans['Quarter'] = disbursedloans['Disbursed'].dt.to_period("Q")
					disbursedloans['Client_Id'] = disbursedloans['Client ID'].str.slice(start=-5, step=1,
																						stop=None).astype('int').abs()
					closed = ['Closed', 'Written Off', 'Overpaid']
					closedloans = disbursedloans[(disbursedloans.Status.isin(closed)) & (
						disbursedloans.Disbursed.between('2015-01-01', '2021-04-30'))]
					closedpivot = closedloans.groupby(['Year', 'Quarter', 'Product'])[
						'TRP'].mean().to_frame().reset_index()
					# merging of products
					disbursedloans1 = disbursedloans
					disbursedloans1['Product'].replace(
						{'JIKO': 'BORA', 'B00M': 'BOOM', 'HOME': 'SKH+', 'LPG3': 'LPG2', 'CVS2': 'CNVS', 'SLO2': 'SILO',
						 'PRO4': 'P400', 'TNK': 'TANK', 'GASC': 'COOK'}, inplace=True)
					closedloans1 = disbursedloans1[(disbursedloans1.Status.isin(closed)) & (
						disbursedloans1.Disbursed.between('2015-01-01', '2021-04-30'))]
					closedmergedpivot = closedloans1.groupby(['Product'])['TRP'].mean().to_frame().reset_index()
					closedmergedpivot2 = closedloans1.groupby(['Branch', 'Product'])[
						'TRP'].mean().to_frame().reset_index()

					fig12 = px.bar(closedmergedpivot, x='Product', y='TRP', color='Product', text='TRP', width=1200,
								   height=700)
					fig12.update_traces(texttemplate='%{text:.2s}', textposition='outside')
					fig12.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', showlegend=False)

					fig4 = px.bar(closedmergedpivot2, x="Product", y='TRP', facet_col="Branch", facet_col_wrap=3,
								  color='Product', text='TRP', width=1800, height=1100)
					fig4.update_traces(texttemplate='%{text:.2s}', textposition='outside')
					fig4.update_layout(uniformtext_minsize=6, uniformtext_mode='hide', showlegend=False)

					st.write(fig12)
					st.write(fig4)
				elif task == "Profiles":
					st.subheader("User Profiles")
					user_result = view_all_users()
					clean_db = pd.DataFrame(user_result,columns=["Username","Password"])
					st.dataframe(clean_db)
			else:
				st.warning("Incorrect Username/Password")





	elif choice == "SignUp":
		st.subheader("Create New Account")
		new_user = st.text_input("Username")
		new_password = st.text_input("Password",type='password')

		if st.button("Signup"):
			create_usertable()
			add_userdata(new_user,make_hashes(new_password))
			st.success("You have successfully created a valid Account")
			st.info("Go to Login Menu to login")



if __name__ == '__main__':
	main()