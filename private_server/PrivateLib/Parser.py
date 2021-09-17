import jieba, re
import logging

jieba.setLogLevel(logging.INFO)
jieba.load_userdict('/home/ubuntu/private_server/PrivateLib/userdict.txt')

normal_pattern = re.compile(r'[\u0041-\u005a\u0061-\u007a]+')
pattern = re.compile(r'[^\u4e00-\u9fa5]')

def parse_subject(subject):
    # 精確模式
    normal = re.findall(normal_pattern, subject)
    subject = re.sub(pattern, '', subject)
    seg_list = jieba.lcut(subject)
    for word in normal:
        seg_list.append(word)
    for word in seg_list.copy():
        if len(word) < 2:
            seg_list.remove(word)
    if len(seg_list) <= 0:
        return []
    return list(dict.fromkeys(seg_list))

if __name__ == "__main__":
    subject = "科技部大專學生專題研究計畫申請書初評意見表"
    result = parse_subject(subject)
    print(result)
