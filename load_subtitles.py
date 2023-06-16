"""
"""
def srt_time_to_milliseconds(time_str):
    """
    time_str: <str>, example = 00:00:21,00
    returns: <int>
    """
    rest, ms = time_str.split(",")
    ms = int(ms)

    rest, secs = rest.rsplit(":", 1)
    secs = int(secs)

    hours, mins = rest.rsplit(":", 1)
    mins = int(mins)
    hours = int(hours)

    return 3600000*hours + 60000*mins + 1000*secs + ms 


def milliseconds_to_srt_time(milliseconds):
    """
    milliseconds: <int>
    returns: <str>, example = 00:00:21,000
    """
    assert milliseconds >= 0
    hours = milliseconds // 3600000
    left = milliseconds - hours*3600000
    mins = left // 60000
    left = left - 60000*mins
    secs = left // 1000
    ms = left - secs*1000

    return f"{str(hours).zfill(2)}:{str(mins).zfill(2)}:{str(secs).zfill(2)},{str(ms).zfill(3)}"


def parse_srt_time_string(srt_time):
    """
    srt_time: <str>, example = 00:00:00,000 --> 00:00:21,000
    returns: <float> start time in milliseconds
             <float> end time in milliseconds
    """
    start_time = srt_time.partition(' ')[0]
    end_time = srt_time.rpartition(' ')[2]
    return srt_time_to_milliseconds(start_time), srt_time_to_milliseconds(end_time)


def load_srt_file(srt_path):
    """
    srt_path: pathlib.Path to .srt subtitles file
    returns: <list> of tuples with format: 
             (<int> start time in milliseconds,
              <int> end time in milliseconds,
              <str> text)
    """
    all_info = list()

    with open(srt_path, "r", encoding='utf-8') as srt_file:
        full_file_string = srt_file.read()
    
    for section in full_file_string.split("\n\n"):
        section_lines = section.split("\n")

        if len(section_lines) == 3:
            number = section_lines[0]
            time_string = section_lines[1]
            text = section_lines[2]
            start, end = parse_srt_time_string(time_string)
            all_info.append((start, end, text))

    return all_info


def load_vtt_file(vtt_path):
    """
    """
    raise NotImplementedError()


def load_txt_file(txt_path):
    """
    """
    raise NotImplementedError()


def find_text_and_index_at_time(loaded_subtitles, time, start_index=0):
    """ This is a valid but slow way of searching through all the time ranges.

    https://en.wikipedia.org/wiki/Interval_tree
    To achieve an efficient search, an interval tree can be constructed.

    """
    if start_index < 0:
        start_index = 0

    active_index = start_index
    for start_time, end_time, text in loaded_subtitles[start_index:]:
        if end_time > time >= start_time:
            return text, active_index
        active_index += 1

    return None, None
