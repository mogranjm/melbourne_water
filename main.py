import pandas as pd
import requests
from bs4 import BeautifulSoup

url = "https://www.melbournewater.com.au/water-data-and-education/water-facts-and-history/why-melbournes-water-tastes-great/testing-water"

def download(target_url):
	headers = {'Accept-Language': 'en-US,en;q=0.5'}

	r = requests.get(target_url, headers)
	soup = BeautifulSoup(r.content, 'html.parser')

	html_table = str(soup.find_all('table'))[1:].encode('ascii', 'ignore')
	return html_table

def process_table(html_table):
	data = pd.read_html(html_table)[0]
	data = data[['Parameter/ source', 'Silvan', 'Winneke']].set_index('Parameter/ source')
	data = data.filter(items=[
		'pH (units)',
		'Calcium',
		'Magnesium',
		'Sodium',
		'Total alkalinity as CaCO3',
		'Hardness',
		'Zinc'
	], axis=0)

	silvan = data.Silvan.str.split('-', expand=True).replace({'<0.001': '0'}, regex=True).astype('float')
	winneke = data.Winneke.str.split('-', expand=True).replace({'<0.001': '0'}, regex=True).astype('float')
	data['Silvan'] = silvan.mean(axis=1)
	data['Winneke'] = winneke.mean(axis=1)

	data = data.T
	data['Bicarbonate'] = data['Total alkalinity as CaCO3'] * 1.22

	data.loc['mixture_5050'] = data.mean()

	return data

if __name__ == '__main__':
	data = download(url)
	result = process_table(data)
	print(result)