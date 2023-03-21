# University Scraper

### Description
This is a web scraper written in python which goes trough the university rankings on [The Guardian](https://www.theguardian.com/education/ng-interactive/2022/sep/24/the-guardian-university-guide-2023-the-rankings) and puts them in an DynamoDB table on AWS, it also goes through each university page on the ranking website and collects the website link for the given university to be stored alongside the other data.

This program was made to work alongside another project ([StudentTools](https://github.com/win20/student-tools)) which will be using this data to implement a 'university finder' feature.

### Languages used
- **Python** for the main app
- **Typescript** for the AWS CDK infrastructure (sets up the DynamoDB table)
