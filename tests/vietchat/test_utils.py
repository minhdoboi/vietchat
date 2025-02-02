

from vietchat.utils import extract_think


def test_clean_response():
  assert extract_think("<think>ok1</think>yes") == ("ok1", "yes")
  assert extract_think("ok2</think>yes") == ("ok2", "yes")
  assert extract_think("""<think>ok3
                        </think>
                        yes""") == ("ok3", "yes")
  assert extract_think("yes") == (None, "yes")