from math import sqrt


def test_grouped_stack_line(grouped_stack_line):
    assert grouped_stack_line.hits == 3
    assert grouped_stack_line.sum == 60
    assert grouped_stack_line.standard_deviation == sqrt(200)
    assert grouped_stack_line.hits_percentage == 0.5
    assert grouped_stack_line.percentage == 0.6
    assert grouped_stack_line.average == 20
