from assess_complexity import analyze_file
import json
import os


def main():
    here = os.path.dirname(__file__)
    sample = os.path.join(here, 'examples', 'example2.c')
    res = analyze_file(sample)
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
