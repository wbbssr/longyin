import requests
import json
import os
import csv

class Question:
    def __init__(self, question_id: str) -> None:
        self.question_id = question_id

    def get_answers(self) -> list[map]:
        url = f"https://www.zhihu.com/api/v4/questions/{self.question_id}/feeds?limit=50&include=content,admin_closed_comment"
        response = requests.get(url).json()

        data = response['data']
        paging = response['paging']
        while not paging['is_end']:
            response = requests.get(paging['next'].replace("limit=5", "limit=50")).json()
            data.extend(response['data'])
            paging = response['paging']

        self.title = data[0]['target']['question']['title']
        self.count = len(data)

        return sorted(data, key=lambda d: d['target']['created_time'], reverse=True)

    def get_question_title(self, data: map) -> str:
        return data['target']['question']['title']
    
    def save(self):
        data = self.get_answers()
        file_path = os.path.expanduser(f'./{self.title}.json')

        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    updated_rows = []
    with open('questions.csv', mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            q = Question(row[0])
            q.save()
            print(f"Saved {q.count} answers for {q.title}")

            if len(row) == 1:
                row.append(q.title)
            updated_rows.append(row)

    with open('questions.csv', 'w', encoding='utf-8') as file:
        csv_writer = csv.writer(file, delimiter=',')
        csv_writer.writerows(updated_rows)