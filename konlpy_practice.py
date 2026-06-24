# PyTorch 기반 한국어 워드 클라우드 과제

# 정규 표현식을 사용하기 위한 re 모듈
import re
# 단어 빈도 계산
from collections import Counter
# Pytorch 텐서 처리
import torch
# 표 형태 데이터 처리
import pandas as pd
# 그래프 출력
import matplotlib.pyplot as plt
from wordcloud import wordcloud
# 한국어 형태소 분석
from konlpy.tag import Okt
# import os

# 1. 텍스트 수집########
# data 폴더에서 불러오기
# 구분자를 탭(\t) 으로 임의 지정하여 한 줄 통째로 불러옴
with open('data/news_title.txt', 'r', encoding='utf-8') as f:
    # 파일의 모든 내용을 하나의 문자열로 읽어옴
    raw_text = f.read()

# 2. 텍스트 정제###########
# 합쳐진 하나의 문자열에서 한글과 공백만 남기고 나머지는 제거
clean_text = re.sub(r'[^ㄱ-ㅎㅏ-ㅣ가-힣]', " ", raw_text)
print(clean_text[:100])

# 3. 형태소 분석기 생성
# Okt는 한국어 문장에서 명사, 동사, 형용사 분리할 수 있음.
okt = Okt()

 # 4. 명사 추출
 # nouns() 함수는 문장에서 명사만 추출
nouns = okt.nouns(clean_text)

# 의미 없는 단어나 특정 출처 단어 제외
stop_words = ['source', '한국', '월드컵', '경기', '내일', '올해', '때문', '중계', '남아공'] # 제외할 단어들

 # 한 글자 단어는 의미가 약한경우가 많아 두 글자 이상만 남김.
final_nouns = [noun for noun in nouns if len(noun) > 1 and noun not in stop_words]
noun_counts = Counter(final_nouns)
print(noun_counts.most_common(10))

 # 5. 단어를 숫자 ID로 변환
 # 중복을 제거한 단어 목록을 정렬하여 vocab
vocab = sorted(set(final_nouns))

# 단어를 숫자 인덱스로 바꾸기 위한 dictionary
word_to_id = {word: i for i, word in enumerate(vocab)}

# 각 명사를 숫자 id로 변환
word_ids = [word_to_id[word] for word in final_nouns]

# 숫자 ID 리스트를 PyTorch 텐서로 변환
word_ids_tensor = torch.tensor(word_ids)

# 6. Pytorch 로 단어 빈도 계산
# torch.bincount()는 각 숫자 ID가 몇 번 나왔는지 계산
word_count_tensor = torch.bincount(word_ids_tensor)

# pytorch 텐서를 파이썬 딕셔너리로 변환
word_freq = {
    vocab[i]: int(word_count_tensor[i].item())
    for i in range(len(vocab))
}

# 빈도수가 높은 순서대로 정렬
word_freq = dict(sorted(word_freq.items(), key=lambda item: item[1], reverse=True))
print(word_freq)


# 7. pandas로 상위 단어 확인
word_freq_series = pd.Series(word_freq)

# 8. Font 경로
font_path = 'C:/Windows/Fonts/malgun.ttf'

# 8. 워드 클라우드
wordcloud = wordcloud.WordCloud(font_path=font_path, width=800, height=400, background_color='white').generate_from_frequencies(word_freq)
plt.figure(figsize=(10, 6))
plt.imshow(wordcloud)
plt.axis('off')
plt.show()
