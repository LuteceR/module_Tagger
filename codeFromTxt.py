from simpletransformers.seq2seq import Seq2SeqModel
import os

def reload_model():
    model_reloaded = Seq2SeqModel(
        encoder_decoder_type="mbart",
        encoder_decoder_name="mbart_pos",
    )
    return model_reloaded

def extract_tags_from_files(folder_path):
    """Основная функция для обработки отчетов"""
    if not os.path.exists(folder_path):
        print(f"Папка не существует: {folder_path}")
        return
    print(f"Обработка папки: {folder_path}")
    print("-" * 50)

    for root, dirs, files in os.walk(folder_path):
        for dir in dirs:
            report_file = root + '\\' + dir + '\\' + 'отчет.txt'
            if not os.path.exists(report_file):
                continue
            print(f"\nПапка: {dir}")
            print(f"Обработка файла: {report_file}")
            text = ''
            with open(report_file, 'r', encoding='utf-8') as file:
                text = file.read()

            """
            здесь основная часть
            текст очищается от лишнего
            далее разбивается на чнки (по 4 предложения в данном случае)
            затем каждый чанк обрабатывается моделью -> получается размеченный текст
            из размеченного текста выделяются теги
            """

            text = clean_text(text)
            text_chunks = split_into_chunks(text, chunk_size=4)

            tags = []
            for chunk in text_chunks:
                predicted_text = model.predict([chunk])
                tags += extract_tags1(predicted_text[0])
                
            """
            """

            print(list(set(tags)))
            with open(root + '\\' + dir + '\\' + 'теги.txt', 'w', encoding='utf-8') as file:
                for tag in tags:
                    file.write(tag + '\n')

model = reload_model()
extract_tags_from_files(PATH4)