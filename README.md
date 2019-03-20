# PyCoinsAggregator

## Requirements:

* **python**==3.5.3
	* A higher version breaks native compatibility with Raspberry Pi.
* **requests**
	* Making rpc calls in nodes.
* **boto3** *Optional*
	* Uploading csv files to AWS s3.

## Usage:

This software is still in test and development phase. It has just been tested with a Dash Core node.

1. Download [Dash Core](https://www.dash.org/downloads/) node.
2. Add the following to dash.conf:
	```
	listen=1
	server=1
	daemon=1
	rpcuser=[any user name you wish]
	rpcpassword=[any password you wish]
	rpcallowip=127.0.0.1
	```

3. Run dashd.
4. In the root of your pycoinsaggregator repository add the following files:
	* `dash.txt`:
		```
		rpcuser=[same user as in dash.conf]
		rpcpassword=[same password as in dash.conf]
		```
	* `aws.txt` (optional):
		```
		id=[AWS ID]
		secret=[AWS SECRET KEY]
		bucket=[The name of your bucket]
		path=[the path of your files within your bucket]
		```
5. Run:
	`python3 test.py [options]`
	* Options:
		* no_aws: remove AWS uploads.

6. The `test.py script will start:
	* Dash aggregation process. It will dump two csv files:
		* `dash_daily.csv` with all daily aggregated values updated every day.
		* `dash_24h.csv` with the last 24h data updated every 20 minutes.
	* AWS Uploader processes. A process for each csv file.
7. The script `test.py` has been designed to support continuos run on a Raspberry Pi.

