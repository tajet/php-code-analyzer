#!/bin/python
# -*- coding: utf-8 -*-

from optparse import OptionParser
import os
import sys
import re

# Datei sicher offnen
def open_file(f):
    try:
        fd = open(f, "r")
    except IOError as e:
        print("Error: ", e)
        sys.exit(1)
    else:
        lines = []
        with fd:
            lines = [l.strip() for l in fd.readlines()]
            return lines

# Highlighting der Problemvariable
def highlight_substring(s, sub_s, color):
    color_start = color
    color_end = "\033[m"
    var_start = s.index(sub_s)
    var_end = var_start + len(sub_s)
    return s[:var_start] + color_start + s[var_start:var_end] + color_end + s[var_end:]

# Ausgabe darstellen
def print_output(matches, traces, max_line_num):
    for i, m in enumerate(matches):
        out1 = "\n\t" + str(m[0]) + ": " + m[1] + "\n"

        out1 = highlight_substring(out1, m[2], "\033[33m")
        print(out1)
        for t in traces[i]:
            out2 = ("\t\t{1:{0:d}d}: {2:s}").format(len(str(max_line_num)), t[0], t[1])
            out2 = highlight_substring(out2, m[2], "\033[33m")
            print(out2)

# Problemvariablen verfolgen
def find_traces(matches, lines):
    traces = [[] for i in range(len(matches))]
    
    # Jede Zeile duchgehen
    for i, l in enumerate(lines):
        # Schauen ob Problemvariable aus Treffer enthalten
        for m in matches:
            # Nur nach Variablenaufrufen suchen die vor dem Problem stehen
            if(m[0] > i):
                # Regex zur suche nach Variablennamen
                regex = re.compile('\\%s\\b'%m[2])
                result = regex.search(l)
                if(result):
                    # traces = [Zeilennumer, Zeile]
                    tmp = [i, l]
                    traces[matches.index(m)].append(tmp)
    return traces

# Sucht Zeile für Zeile nach Regex
def find_matches(lines, regex):
    # Speichert die größte Zeilennummer für spätere Ausgabeformatierung
    max_line_num = 0
    # matches = [zeilennummer, trefferzeile, problemvariable]
    matches = []

    # Jede Zeile durchgehen
    for i, l in enumerate(lines):
        # Jede Schwachstelle durchgehen
        for r in regex:
            result = re.search(r, l) 
            if(result):
                # matches = [zeilennummer, trefferzeile, problemvariable]
                tmp = [i, result.group(0), result.group(1)]
                matches.append(tmp)
                max_line_num = i
    return (matches, max_line_num)

# Datei wird auf Schwachstellen/Warnungen analysiert
def analyse_file(f):
    regex = []

    # Suchausdrücke um in Text Warnungen und Schwachstellen finden
    # mysqli_query($con, $sql);
    regex.append(re.compile("mysqli_query ?\(\$.*, *(\$\w+).*\)"))
    # mysql_query($sql);
    # mssql_execute($sql);
    regex.append(re.compile("(m(y|s)sql)_(query|execute) ?\(\$.*\)"))
    # mysql_db_query($con, $sql);
    regex.append(re.compile("mysql_db_query ?\(\$.*, *\$.*\)"))
    # mssql_bind($stmt, '@username',  $bla ,  SQLVARCHAR,  false,  false,  60);
    regex.append(re.compile("mssql_bind ?\(\$.*, *\$.*\)"))
    # odbc_prepare($con, $sql);
    # odbc_execute($stmt, $stuff);
    # odbc_exec($con, $sql);)
    regex.append(re.compile("odbc_(prepare|exec(ute)?) ?\(\$.*, *\$.*\)"))
    # oci_parse($con, $sql);
    # ora_parse($con, $sql);
    regex.append(re.compile("(oci|ora)_parse ?\(\$.*, *\$.*\)"))

    print("\nAnalysing file: " + f)

    # Datei einlesen
    lines = open_file(f)

    # Suche nach Warnungen/Schwachstellen
    (matches, max_line_num) = find_matches(lines, regex)

    # Rückverfolgung der potentiell gefählichen Variablen
    traces = find_traces(matches, lines)

    # Ausgabe und Formatierung  der Ergebnisse
    print_output(matches, traces, max_line_num)

def main():
    # OptionParser für Kommandozeilenargumente
    parser = OptionParser()

    parser.add_option("-f", "--file", dest="file", help="file to analyse.")
    parser.add_option("-d", "--dir", dest="directory", \
                        help="directory to analyse.")

    (options, args) = parser.parse_args()

    directory = options.directory

    # Ordner analysieren
    if(directory):
        # Jede Datei in einem Ordner durchgehen und analysieren    
        for f in os.listdir(directory):
            path_to = directory + "/" + f
            analyse_file(path_to)

    # Einzelne Datei analysieren
    if(options.file):
        analyse_file(options.file)

if __name__ == "__main__":
    main()
