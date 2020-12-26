import streamlit as st
import pandas as pd
import json
import csv
import requests
import time
import os


def get_api_key():
	if 'api_key.txt' in os.listdir():
		api_key = open('api_key.txt', 'r').read()
		return api_key
	

def select_file(path='.'):
	files = os.listdir(path)
	placeholder = ''
	files.insert(0, placeholder)
	file_option = st.selectbox('Select file', files)
	return file_option


def read_emails(fname):
	emails = []
	with open(fname, 'r') as infile:
		reader = csv.reader(infile)
		for row in reader:
			emails.append(row)

	emails = list(map(lambda x: x[0], emails))
	return emails

	# Alternatively: depending on structure of the file
	# emails = pd.read_csv('emails.csv')['Email']


def request_emails():
	example = 'xxxxxxx@email.com'
	email = st.text_input('Email address to search', example)
	if 'batch.csv' in os.listdir():
		emails = read_emails('batch.csv')
	else:
		emails = []
	if email != example:
		emails.append(email)
		y_n = ['', 'yes', 'no']
		start_option = st.selectbox('Do you want search your emails now?', y_n)
		if start_option == 'yes':
			batch_emails(emails)
			emails = read_emails('batches.csv')
			return emails
		elif start_option == 'no':
			batch_emails(emails)
			st.write('To add more emails, simply refresh the page.')


def batch_emails(emails):
	batch = [[email] for email in emails]
	with open('batches.csv', 'a') as outfile:
		writer = csv.writer(outfile)
		for email in batch:
			writer.writerow(email)


def scan_breaches(emails):
	compromised = {}
	for email in emails:
		service = 'breachedaccount'
		# parameter = '{}?domain=udacity.com'.format(email)
		parameter = email
		url = 'https://haveibeenpwned.com/api/v3/{}/{}'.format(service, parameter)
		headers = {'hibp-api-key': api_key,
				   'user-agent': 'pwnage'}
		response = requests.get(url, headers=headers)
		if response.text:
			compromised[email] = json.loads(response.text)
		time.sleep(3)
	return compromised


def get_breach_count(compromised):
	emails = list(compromised.keys())
	breach_count = []
	for email in emails:
		breach_count.append(len(compromised[email]))
	return sum(breach_count)


def get_email_count(compromised):
	emails = list(compromised.keys())
	return len(emails)


def prettify_results(compromised):
	emails = list(compromised.keys())
	prettified = []
	for email in emails:
		breaches = compromised[email]
		for breach in breaches:
			prettified.append([email, breach['Name']])
	return prettified


def write_csv(data):
	df = pd.DataFrame(data, columns=['Email', 'Breach'])
	df.to_csv('breaches.csv', index=False)



def run_main(emails):
	compromised = scan_breaches(emails)
	breach_count = get_breach_count(compromised)
	email_count = get_email_count(compromised)
	st.write('You have found {} breaches for {} accounts'.format(breach_count, email_count))
	prettified_results = prettify_results(compromised)
	st.write('You have prettified your results')
	write_csv(prettified_results)
	st.write('You have have update {}'.format('breaches.csv'))


if __name__ == '__main__':
	api_key = get_api_key()
	print(api_key)
	if api_key:
		fname = select_file()
		print('?')
		if fname:
			st.write('You selected {}'.format(fname))
			emails = read_emails(fname)
			# parameters = []
			# parameter_options = st.selectbox(parameters)
			run_main(emails)
	else:
		api_key = st.text_input('Enter your API key', '')
		if api_key:
			emails = request_emails()
			if emails:
				run_main(emails)
