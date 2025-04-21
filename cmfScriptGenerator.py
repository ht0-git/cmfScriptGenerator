import os
from pathlib import Path

FACTIONS_FILE = Path("factions.txt")
MAIN_SCRIPT = Path("cmf_script__main.txt")
TEXT_FILE = Path("text.txt")

g_orig_faction_list = []


def get_any_char_to_continue():
    input("Enter any character: ")


def get_faction_list():
    if not FACTIONS_FILE.exists():
        print("Can't read factions.txt")
        get_any_char_to_continue()
        exit(1)

    with FACTIONS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            g_orig_faction_list.extend(line.strip().split())

    return bool(g_orig_faction_list)


def print_faction_list():
    for faction in g_orig_faction_list:
        print(faction)


def remove_if_exists(path):
    if path.exists():
        path.unlink()


def create_main_script():
    remove_if_exists(MAIN_SCRIPT)

    with MAIN_SCRIPT.open("w", encoding="utf-8") as file:
        file.write(
            "script\n\ndeclare_persistent_counter cmf_first_time_setup\n"
            "declare_persistent_counter cmf_first_playercontrol_faction\n\n"
            "if I_CompareCounter cmf_first_time_setup = 0\n"
        )

        for i, faction in enumerate(g_orig_faction_list):
            file.write(f"\n\tif TestFaction {faction}\n\t\tset_counter cmf_first_playercontrol_faction {i+1}\n\tend_if")

        file.write("\n\n\tset_counter cmf_first_time_setup 1\n\nend_if\n\n")
        file.write("if I_CompareCounter cmf_first_time_setup = 1\n")

        for i, faction in enumerate(g_orig_faction_list):
            file.write(f"\n\tif I_CompareCounter cmf_first_playercontrol_faction = {i+1}\n")
            file.write(f"\t\tinclude_script cmf_script_{faction}.txt\n\tend_if")

        file.write("\n\nend_if\n\nend_script")
        
        print("cmf_script__main.txt - OK")


def generate_first_setup(file, curr_index):
    file.write(
        "script\n\n"
        "suspend_during_battle on\n\n"
        "declare_persistent_counter cmf_first_setup\n\n"
        "if I_CompareCounter cmf_first_setup = 0\n"
    )

    for i, faction in enumerate(g_orig_faction_list):
        file.write(f"\tdeclare_persistent_counter cmf_{faction}\n")

    file.write(
        "\n\tdeclare_persistent_counter cmf_force_diplomacy_option\n\n"
        "\tdeclare_counter cmf_plays_force_diplomacy_option_question\n"
        "\tdeclare_counter cmf_force_diplomacy_option_asked\n"
        "\tdeclare_counter cmf_force_diplomacy_option_answered\n"
        "\tdeclare_counter cmf_plays_force_diplomacy_option_output\n\n"
    )

    for i, faction in enumerate(g_orig_faction_list):
        if i == curr_index:
            continue
        file.write(
            f"\tdeclare_counter cmf_plays_{faction}_question\n"
            f"\tdeclare_counter cmf_{faction}_asked\n"
            f"\tdeclare_counter cmf_{faction}_answered\n"
            f"\tdeclare_counter cmf_plays_{faction}_output\n\n"
        )

    file.write(f"\tset_counter cmf_{g_orig_faction_list[curr_index]} 1\n")
    file.write("end_if\n\n")


def generate_questions(file, curr_index):
    file.write(
        "while I_CompareCounter cmf_first_setup = 0\n\n"
        "\tif I_CompareCounter cmf_force_diplomacy_option_asked = 0\n"
        "\t\tmessage_prompt\n"
        "\t\t{\n"
        "\t\t\tflag_counter cmf_plays_force_diplomacy_option_question\n"
        "\t\t\tresult_counter cmf_plays_force_diplomacy_option_output\n\n"
        "\t\t\ttitle CMF_PLAYS_FORCE_DIPLOMACY_OPTION_TITLE\n"
        "\t\t\tbody CMF_PLAYS_FORCE_DIPLOMACY_OPTION_BODY\n\n"
        "\t\t\timage adoption\n"
        "\t\t}\n"
        "\t\tset_counter cmf_force_diplomacy_option_asked 1\n"
        "\tend_if\n\n"
        "\tmonitor_event ScriptPromptCallback I_CompareCounter cmf_plays_force_diplomacy_option_question == 1\n"
        "\t\tif I_CompareCounter cmf_plays_force_diplomacy_option_output == 1\n"
        "\t\t\tset_counter cmf_force_diplomacy_option 1\n"
        "\t\tend_if\n"
        "\t\tif I_CompareCounter cmf_plays_force_diplomacy_option_output == 0\n"
        "\t\t\tset_counter cmf_force_diplomacy_option 2\n"
        "\t\tend_if\n\n"
        "\t\tset_counter cmf_plays_singleplayer_hotseat_question 0\n"
        "\t\tset_counter cmf_force_diplomacy_option_answered 1\n"
        "\tend_monitor\n\n"
    )

    prev_valid_faction = None

    for i, faction in enumerate(g_orig_faction_list):
        if i == curr_index:
            continue

        file.write(f"\tif I_CompareCounter cmf_{faction}_asked = 0\n\tand I_CompareCounter ")

        if prev_valid_faction is None:
            file.write("cmf_force_diplomacy_option_answered = 1\n")
        else:
            file.write(f"cmf_{prev_valid_faction}_answered = 1\n")

        f_name_upper = faction.upper()
        file.write(
            f"\t\tmessage_prompt\n"
            f"\t\t{{\n"
            f"\t\t\tflag_counter cmf_plays_{faction}_question\n"
            f"\t\t\tresult_counter cmf_plays_{faction}_output\n\n"
            f"\t\t\ttitle CMF_PLAYS_{f_name_upper}_TITLE\n"
            f"\t\t\tbody CMF_PLAYS_{f_name_upper}_BODY\n\n"
            f"\t\t\timage adoption\n"
            f"\t\t}}\n"
            f"\t\tset_counter cmf_{faction}_asked 1\n"
            f"\tend_if\n\n"
        )

        file.write(
            f"\tmonitor_event ScriptPromptCallback I_CompareCounter cmf_plays_{faction}_question == 1\n"
            f"\t\tif I_CompareCounter cmf_plays_{faction}_output == 1\n"
            f"\t\t\tset_counter cmf_{faction} 1\n"
            f"\t\tend_if\n"
            f"\t\tif I_CompareCounter cmf_plays_{faction}_output == 0\n"
            f"\t\t\tset_counter cmf_{faction} 0\n"
            f"\t\tend_if\n\n"
        )

        is_last = (
            i == len(g_orig_faction_list) - 1 or
            (i + 1 == curr_index and curr_index == len(g_orig_faction_list) - 1)
        )
        if is_last:
            file.write(
                "\t\tset_counter cmf_first_setup 1\n"
                "\tend_monitor\n\n"
                "end_while\n\n"
            )
        else:
            file.write(
                f"\t\tset_counter cmf_plays_{faction}_question 0\n"
                f"\t\tset_counter cmf_{faction}_answered 1\n"
                f"\tend_monitor\n\n"
            )

        prev_valid_faction = faction


def generate_not_alive_checks(file, curr_index):
    vec = g_orig_faction_list[:]
    temp_vec = g_orig_faction_list[:]

    if curr_index:
        vec[0], vec[curr_index] = vec[curr_index], vec[0]
        temp_vec[0], temp_vec[curr_index] = temp_vec[curr_index], temp_vec[0]

    for i, faction in enumerate(vec):
        min_idx = 0
        for n in range(1, len(g_orig_faction_list)):
            file.write(f"monitor_event FactionTurnEnd FactionType {faction}\n")
            file.write(f"and I_CompareCounter cmf_{temp_vec[n]} = 1\n")

            for m in range(min_idx):
                file.write(f"and not FactionIsAlive {temp_vec[m + 1]}\n")

            file.write(f"and FactionIsAlive {temp_vec[n]}\n")
            file.write(f"\tconsole_command control {temp_vec[n]}\n")
            file.write("end_monitor\n\n")
            min_idx += 1

        temp_vec = temp_vec[1:] + temp_vec[:1]


def generate_goto_capital(file, curr_index):
    for faction in g_orig_faction_list:
        file.write(
            f"monitor_event FactionTurnStart FactionType {faction}\n"
            f"and I_CompareCounter cmf_{faction} = 1\n"
            f"and FactionIsAlive {faction}\n"
            "\tconsole_command force_diplomacy off\n"
            "\tset_counter cmf_diplomacy_asked 0\n"
            "\tsnap_strat_camera 0, 156\n"
            "\tzoom_strat_camera 0.8\n"
            f"\tconsole_command go_to_capital {faction}\n"
            "end_monitor\n\n"
        )


def generate_diplomacy_script(file):
    file.write("declare_persistent_counter cmf_switch_diplomacy\n\n")
    file.write("declare_counter cmf_switch_diplomacy_asked\n")
    file.write("declare_counter cmf_switch_diplomacy_question\n")
    file.write("declare_counter cmf_switch_diplomacy_output\n")
    file.write("declare_counter cmf_switch_diplomacy_answered\n\n")

    file.write("if_not I_CompareCounter cmf_switch_diplomacy == 2\n")
    file.write("\tinc_counter cmf_switch_diplomacy 1\n")
    file.write("end_if\n\n")

    file.write("if I_CompareCounter cmf_switch_diplomacy = 2\n")
    file.write("\twhile I_CompareCounter cmf_switch_diplomacy_answered = 0\n")
    file.write("\t\tif I_CompareCounter cmf_switch_diplomacy_asked = 0\n")
    file.write("\t\t\tmessage_prompt\n")
    file.write("\t\t\t{\n")
    file.write("\t\t\t\tflag_counter cmf_switch_diplomacy_question\n")
    file.write("\t\t\t\tresult_counter cmf_switch_diplomacy_output\n\n")
    file.write("\t\t\t\ttitle CMF_PLAYS_FORCE_DIPLOMACY_OPTION_TITLE\n")
    file.write("\t\t\t\tbody CMF_PLAYS_FORCE_DIPLOMACY_OPTION_BODY\n\n")
    file.write("\t\t\t\timage adoption\n")
    file.write("\t\t\t}\n")
    file.write("\t\t\tset_counter cmf_switch_diplomacy_asked 1\n")
    file.write("\t\tend_if\n\n")

    file.write("\t\tmonitor_event ScriptPromptCallback I_CompareCounter cmf_switch_diplomacy_question == 1\n")
    file.write("\t\t\tif I_CompareCounter cmf_switch_diplomacy_output == 1\n")
    file.write("\t\t\t\tset_counter cmf_force_diplomacy_option 1\n")
    file.write("\t\t\tend_if\n")
    file.write("\t\t\tif I_CompareCounter cmf_switch_diplomacy_output == 0\n")
    file.write("\t\t\t\tset_counter cmf_force_diplomacy_option 2\n")
    file.write("\t\t\tend_if\n\n")
    file.write("\t\t\tset_counter cmf_switch_diplomacy_answered 1\n")
    file.write("\t\tend_monitor\n")
    file.write("\tend_while\n")
    file.write("end_if\n\n")

    file.write("declare_counter cmf_loop\n")
    file.write("declare_counter cmf_diplomacy_asked\n")
    file.write("declare_counter cmf_diplomacy_question\n")
    file.write("declare_counter cmf_diplomacy_output\n\n")

    file.write("while I_CompareCounter cmf_loop = 0\n")
    file.write("\tif I_AgentSelected diplomat\n")
    file.write("\tand I_CompareCounter cmf_diplomacy_asked = 0\n")
    file.write("\tand I_CompareCounter cmf_force_diplomacy_option = 1\n")
    file.write("\t\tmessage_prompt\n")
    file.write("\t\t{\n")
    file.write("\t\t\tflag_counter cmf_diplomacy_question\n")
    file.write("\t\t\tresult_counter cmf_diplomacy_output\n\n")
    file.write("\t\t\ttitle CMF_FORCEDIPLOMACY_TITLE\n")
    file.write("\t\t\tbody CMF_FORCEDIPLOMACY_BODY\n\n")
    file.write("\t\t\timage adoption\n")
    file.write("\t\t}\n")
    file.write("\t\tset_counter cmf_diplomacy_asked 1\n")
    file.write("\tend_if\n\n")

    file.write("\tmonitor_event ScriptPromptCallback I_CompareCounter cmf_diplomacy_question == 1\n")
    file.write("\t\tif I_CompareCounter cmf_diplomacy_output == 1\n")
    file.write("\t\t\tconsole_command force_diplomacy accept\n")
    file.write("\t\tend_if\n")
    file.write("\t\tset_counter cmf_diplomacy_question 0\n")
    file.write("\tend_monitor\n")
    file.write("end_while\n\n")
    file.write("end_script")

def create_additional_scripts():
    for i, faction in enumerate(g_orig_faction_list):
        filename = f"cmf_script_{faction}.txt"
        path = Path(filename)
        remove_if_exists(path)

        with path.open("w", encoding="utf-8") as file:
            generate_first_setup(file, i)
            generate_questions(file, i)
            generate_not_alive_checks(file, i)
            generate_goto_capital(file, i)
            generate_diplomacy_script(file)

        print(f"{filename} - OK!")


def create_translation_text_file():
    remove_if_exists(TEXT_FILE)

    with TEXT_FILE.open("w", encoding="utf-8") as file:
        for faction in g_orig_faction_list:
            upper_f = faction.upper()
            file.write(
                f"{{CMF_PLAYS_{upper_f}_TITLE}} {{{upper_f}}}\n"
                f"{{CMF_PLAYS_{upper_f}_BODY}} Will {{{upper_f}}} be controlled by the player??\n"
            )

        file.write(
            "{CMF_FORCEDIPLOMACY_TITLE} Force Diplomacy\n"
            "{CMF_FORCEDIPLOMACY_BODY} Do you want to force a diplomatic answer?\\n This will make the AI accept anything you ask for, for the rest of this turn. Please only use this when you need to make a deal with another faction you control.\n"
            "{CMF_PLAYS_FORCE_DIPLOMACY_OPTION_TITLE} Choose diplomacy options\n"
            "{CMF_PLAYS_FORCE_DIPLOMACY_OPTION_BODY} Do you want to enable forced diplomacy?\\n This means everytime you click on a diplomat you will get a message asking you if you want the AI to accept every diplomatic offer you make. For example this can be used to make a deal with another faction you control.\\n Or do you want to disable this option? So you will not get annoyed by a message appearing every time you click on a diplomat.\\n However you will not be able to use this feature.\\n \\n Accept to enable the Forced Diplomacy option\\n Decline to disable this feature."
        )

    print("text.txt - OK!")


def main():
    print('Reading factions from the file "factions.txt":')

    if not get_faction_list():
        print("Can't find factions! File empty?")
        get_any_char_to_continue()
        return

    print_faction_list()

    user_input = input("Generate scripts ('y' for yes)? ").strip().lower()
    if user_input != 'y':
        return

    create_main_script()
    create_additional_scripts()
    create_translation_text_file()

    get_any_char_to_continue()


if __name__ == "__main__":
    main()
