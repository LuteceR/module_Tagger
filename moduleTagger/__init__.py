class moduleTagger:
    def __init__(self):
        """
        Создание объекта Module Tagger
        """

        self.text = ""
    
    def __call__(self):
        return self
    
    def read_clean_text(self, text: str):
        """
        Чтение текста для поиска тегов
        
        :param text: Текст
        :type text: str
        """

        print("reading...")
        
        #...