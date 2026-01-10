from simpletransformers.seq2seq import Seq2SeqModel
import os

class moduleTagger:
    def __init__(self, flag_use_cuda = True):
        """
        Создание объекта Module Tagger
        """
        self.text = ""
        
        try:
            model_reloaded = Seq2SeqModel(
                encoder_decoder_type="mbart",
                encoder_decoder_name="mbart_pos",
                use_cuda = flag_use_cuda
            )

            self.model = model_reloaded
            print("Успешная инициализация модели")
        except Exception as ex: 
            print(f"Не удалось инициализировать модель\n{ex}")
            
    
    def __call__(self):
        return self
    
    def read_clean_text(self, text: str):
        """
        Чтение текста
        
        :param text: текст
        :type text: str
        """

        self.text = text