import streamlit as st
import pandas as pd
import json
import csv
import requests
import time
import os


def select_file(path='.'):
	files = os.listdir(path)
	placeholder = 'Choose your email file'
	files.insert(0, placeholder)
	file_option = st.selectbox('Select file', files)
	return file_option


def retrieve_emails(fname):
	emails = []
	with open(fname, 'r') as infile:
		reader = csv.reader(infile)
		for row in reader:
			emails.append(row)

	emails = list(map(lambda x: x[0], emails))
	return emails

# Alternatively: depending on structure of the file
# emails = pd.read_csv('emails.csv')['Email']


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

if __name__ == '__main__':
	api_key = open('api_key.txt', 'r').read()
	fname = select_file()
	if fname != 'Choose your email file':
		st.write('You selected {}'.format(fname))
		emails = retrieve_emails(fname)
		# parameters = []
		# parameter_options = st.selectbox(parameters)
		compromised = scan_breaches(emails)
		breach_count = get_breach_count(compromised)
		email_count = get_email_count(compromised)
		st.write('You have found {} breaches for {} accounts'.format(breach_count, email_count))
		prettified_results = prettify_results(compromised)
		st.write('You have prettified your results')
		write_csv(prettified_results)
		st.write('You have have update {}'.format('breaches.csv'))