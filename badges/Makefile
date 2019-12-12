.DEFAULT_GOAL := all

badges.pdf: badges.tex all-participants.tex
	lualatex badges.tex

badges_summer_school.pdf: badges_summer_school.tex summer-school-participants.tex
	lualatex badges_summer_school.tex

all: badges.pdf badges_summer_school.pdf
