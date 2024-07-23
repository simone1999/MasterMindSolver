from functools import cache


def get_all_solutions() -> tuple[tuple[int, int, int, int], ...]:
    solutions = []
    for first_colour in range(6):
        for second_colour in range(6):
            if second_colour == first_colour:
                continue
            for third_colour in range(6):
                if third_colour == first_colour or third_colour == second_colour:
                    continue
                for forth_colour in range(6):
                    if forth_colour == first_colour or forth_colour == second_colour or forth_colour == third_colour:
                        continue
                    solutions.append((first_colour, second_colour, third_colour, forth_colour))
    return tuple(solutions)


def prune_solutions(solutions: tuple[tuple[int, int, int, int], ...], move: tuple[int, int, int, int], validation: tuple[int, int]) -> tuple[tuple[int, int, int, int], ...]:
    # this is slow and taking over 50% of the entire runtime. Not the still_valid function, but the list comprehension
    return tuple([solution for solution in solutions if still_valid(solution=solution, move=move, validation=validation)])


@cache
def still_valid(solution: tuple[int, int, int, int], move: tuple[int, int, int, int], validation: tuple[int, int]) -> bool:
    num_same_position = [solution[i] == move[i] for i in range(4)].count(True)
    if num_same_position != validation[0]:
        return False
    num_same_colour = [colour in move for colour in solution].count(True)
    if num_same_colour != validation[1]:
        return False
    return True


def get_validator_moves(move: tuple[int, int, int, int], possible_solutions: tuple[tuple[int, int, int, int], ...]) -> tuple[tuple[int, int], ...]:
    possible_validations = set()
    for solution in possible_solutions:

        possible_validations.add(get_hits(move=move, solution=solution))
    return tuple(possible_validations)


@cache
def get_hits(move: tuple[int, int, int, int], solution: tuple[int, int, int, int]) -> tuple[int, int]:
    exact_hits: int = sum(move[i] == solution[i] for i in range(4))
    hits: int = sum(colour in solution for colour in move)
    return exact_hits, hits


@cache
def get_min_max_depth(possible_solutions: tuple[tuple[int, int, int, int], ...], first_move=False) -> tuple[int, tuple[int, int, int, int]]:
    move_depths = []
    moves_to_try = possible_solutions if not first_move else ((0, 1, 2, 3), )
    for move in moves_to_try:
        validation_depths = []
        for validation in get_validator_moves(move=move, possible_solutions=possible_solutions):
            if validation == (4, 4):
                validation_depths.append(0)
            else:
                possible_solutions_new = prune_solutions(solutions=possible_solutions, move=move, validation=validation)
                validation_depths.append(get_min_max_depth(possible_solutions=possible_solutions_new)[0] + 1)
        worst_case_depth = max(validation_depths)  # worst case hidden solution
        if worst_case_depth == 0:
            # if we found a branch that guarantees us to win, we don't need to traverse the other branches
            return 0, move
        move_depths.append(worst_case_depth)
    assert len(move_depths) == len(moves_to_try)

    best_move_idx = min(range(len(move_depths)), key=lambda x: move_depths[x])
    assert move_depths[best_move_idx] == min(move_depths)
    return move_depths[best_move_idx], moves_to_try[best_move_idx]


def main():
    print("set [1, 4, 3, 2] means to put the first colour in the first position, forth colour in the second position etc.")
    print()
    print("Let's start:")
    possible_solutions = get_all_solutions()
    first_move = True
    while True:
        turns, move = get_min_max_depth(possible_solutions=possible_solutions, first_move=first_move)
        first_move = False
        move_formatted = [colour + 1 for colour in move]
        if turns == 0:
            print(f"Final move: {move_formatted}")
            break
        print(f"set {move_formatted} and you will win in at most {turns} further turns, there are {len(possible_solutions)} possible solutions left")
        exact_hits = int(input(f"How many exact hits did you get? "))
        assert 0 <= exact_hits <= 4
        if exact_hits == 4:
            print("Congratulations, you won!")
            break
        hits = int(input(f"How many non-exact hits did you get? ")) + exact_hits
        assert hits >= 2, "It is not possible to have less than 2 total hits in the version of the game this bot was created for."
        assert hits <= 4
        possible_solutions = prune_solutions(solutions=possible_solutions, move=move, validation=(exact_hits, hits))


if __name__ == "__main__":
    main()
