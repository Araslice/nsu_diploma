import json
from dotenv import load_dotenv
from tqdm import tqdm
import os

load_dotenv()

class LLMMarker:
    '''
    Для объекта этого класса требуется путь к файлу изначального (неразмеченного) датасета
    '''
    def __init__(self, unmarked_dataset_path):
        self.ud_path = unmarked_dataset_path

    def mark_dataset(self, system_prompt_path, output_folder, max_text_len=0):

        '''
        Размечает тексты в неразмеченном датасете с помощью LLM.
        На вход подаются путь к файлу с системным промптом, папкой с размеченными текстами, максимальная длина неразмеченного текста (опционально).
        На выходе генерируются файлы с размеченными текстами, каждый текст в своём файле 

        '''

        with open(self.ud_path, 'r', encoding='utf-8') as f:
            unmarked_dataset = json.load(f)

        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read()

        i = 0
        prev_marked_texts = 0
        new_marked_texts = 0
        for op_text in unmarked_dataset:
            j = 0
            for orig_text in tqdm(op_text['orig_texts']):

                output_path = f'{output_folder}\op{i}_txt{j}.txt'
                if os.path.exists(output_path):
                    prev_marked_texts += 1
                    continue

                if max_text_len == 0:
                    text_to_mark = orig_text['text']
                else:
                    text_to_mark = orig_text['text'][:max_text_len]

                try:
                    result = 'Something'
                    #TODO: add LLM
                    new_marked_texts += 1
                except Exception as e:
                    print(f'Ошибка в {j}-ом тексте {i}-го текста-опровержения: {e}')
                    result = 'Не удалось разметить'

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result)

                j += 1

            i += 1

        print(f'Ранее размеченных текстов: {prev_marked_texts}\nНовых размеченных текстов: {new_marked_texts}')

    def from_txtfiles_tojson(self, folder_wfiles):

        '''
        Собирает все размеченные тексты в один json-файл.
        На вход подаётся папка с размеченными текстами. 
        На выходе генерируется единый json-файл с удачно (при работе LLM не возникало ошибок) размеченными текстами
        '''

        with open(self.ud_path, 'r', encoding='utf-8') as f:
            unmarked_dataset = json.load(f)

        i = 0
        texts = []

        for op_text in unmarked_dataset:

            for j in tqdm(range(len(op_text['orig_texts']))):

                file_path = f'{folder_wfiles}\op{i}_txt{j}.txt'
                if os.path.exists(file_path) == False:
                    continue

                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                if text == 'Не удалось разметить':
                    continue

                texts.append(text)

            i += 1

        with open('all_marked_texts.json', 'w', encoding='utf-8') as f:
            json.dump(texts, f, ensure_ascii=False, indent=4)

    
if __name__ == '__main__':
    unmarked_dataset_path = os.getenv('UNMARKED_DATASET_PATH')
    fake_marker = LLMMarker(unmarked_dataset_path)
    fake_marker.mark_dataset('system_prompt.txt', 'marked_texts', 1000)
    fake_marker.from_txtfiles_tojson('marked_texts')

        










            