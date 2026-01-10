import os
import argparse
import logging
from typing import Optional
from sci_tagging.core import TagExtractor

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"

def iter_docx(folder_path: str):
    for root, _, files in os.walk(folder_path):
        for fname in files:
            if fname.lower().endswith('.docx'):
                yield os.path.join(root, fname)

def main():
    parser = argparse.ArgumentParser(description="CLI для извлечения тегов из .docx")
    parser.add_argument("--root", required=True, help="Корневая папка с .docx")
    parser.add_argument("--seg-mode", choices=["sentences", "paragraphs", "chars"], default="sentences")
    parser.add_argument("--sent-per-chunk", type=int, default=4)
    parser.add_argument("--para-per-chunk", type=int, default=1)
    parser.add_argument("--chars-per-chunk", type=int, default=2000)
    parser.add_argument("--stride-chars", type=int, default=0)
    parser.add_argument("--preannotated-only", action="store_true")
    parser.add_argument("--model-path", default="mbart_pos", help="Путь к локальной модели mBART")
    parser.add_argument("--eval-batch-size", type=int, default=16)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    model = None
    if not args.preannotated_only:
        # Загрузка локальной модели mBART
        try:
            import torch  # type: ignore
            use_cuda = bool(torch.cuda.is_available())
        except Exception:
            use_cuda = False

        # Отложенный импорт simpletransformers, чтобы режим preannotated-only работал без него
        from simpletransformers.seq2seq import Seq2SeqModel  # type: ignore
        model = Seq2SeqModel(
            encoder_decoder_type="mbart",
            encoder_decoder_name=args.model_path,
            use_cuda=use_cuda,
        )
        try:
            model.args.fp16 = use_cuda
            model.args.eval_batch_size = args.eval_batch_size
        except Exception:
            pass
        logging.info(f"CUDA: {'ON' if use_cuda else 'OFF'}, eval_batch_size={args.eval_batch_size}")

    extractor = TagExtractor(model=model)

    summary_path = os.path.join(args.root, "_tags_index.txt")
    with open(summary_path, "a", encoding="utf-8") as index_file:
        for path in iter_docx(args.root):
            result = extractor.extract_from_path(
                path=path,
                seg_mode=args.seg_mode,
                sentences_per_chunk=args.sent_per_chunk,
                paragraphs_per_chunk=args.para_per_chunk,
                chars_per_chunk=args.chars_per_chunk,
                stride_chars=(args.stride_chars if args.stride_chars > 0 else None),
                preannotated_only=args.preannotated_only,
            )
            rel = os.path.relpath(path, args.root).replace("\\", "/")
            tags_joined = ",".join(result.get("tags", []))
            file_hash = (result.get("meta", {}) or {}).get("file_hash", "")
            line = f"{result.get('supervisors','-')}:{rel}:{tags_joined}:{file_hash}\n"
            index_file.write(line)
            index_file.flush()
            try:
                os.fsync(index_file.fileno())
            except Exception:
                pass
            logging.info(f"{path}: supervisors={result['supervisors']}, tags={len(result['tags'])}")
    logging.info(f"Сводный файл индекса: {summary_path}")

if __name__ == "__main__":
    main()


