PYTHON:=python3

.DEFAULT_GOAL := tex

.PHONY: tex csv letters vouchers update-schedule webapp

tex: xml/db.xml
	$(PYTHON) export_poster.py
	$(PYTHON) export_schedule.py
	$(PYTHON) boa_create_register.py
	$(PYTHON) boa_clusters_and_chairs.py
	$(PYTHON) boa_best_paper.py
	$(PYTHON) boa_semi_and_plenaries.py

xml/db.xml: converia-input/build_xml_db.py converia-input/paper.xml converia-input/EVENT_Agenda.csv converia-input/EVENT_Personenliste.csv converia-input/log.csv converia-input/free_participation.csv converia-input/late_summer_school.csv converia-input/late_dinner.csv converia-input/BOARD_meeting.csv converia-input/OTHERBOARD_meeting.csv 
	cd converia-input; $(PYTHON) build_xml_db.py

app-general/schedule.xml: xml/db.xml app-general/build_schedule.py
	cd app-general; $(PYTHON) build_schedule.py

csv: xml/db.xml other/build_tubs_list.py
	cd other; $(PYTHON) build_tubs_list.py

vouchers: xml/db.xml
	cd vouchers; $(PYTHON) export_dinner_tickets.py
	cd vouchers; $(PYTHON) export_vouchers.py
	make -C $@

badges/summer-school-participants.tex: xml/db.xml badges/build_badges.py
	cd badges; $(PYTHON) build_badges.py

badges/all-participants.tex: xml/db.xml badges/build_badges.py
	cd badges; $(PYTHON) build_badges.py

badges/badges.pdf: badges/build_badges.py badges/badges.tex badges/badges_summer_school.tex badges/all-participants.tex badges/summer-school-participants.tex
	cd badges; $(PYTHON) build_badges.py
	make -C badges

badges: badges/badges.pdf badges/badges_summer_school.pdf

letters/ICCOPT2019_participation-letters.tex: xml/db.xml export_participation_letters.py
	$(PYTHON) export_participation_letters.py

participation_letters/participation-letters.tex: xml/db.xml participation_letters/export_participation_letters.py
	cd participation_letters; $(PYTHON) export_participation_letters.py

participation_letters/summer-school_participation-letters.tex: xml/db.xml participation_letters/export_summerschool_letters.py
	cd participation_letters; $(PYTHON) export_summerschool_letters.py

participation_letters: participation_letters/participation-letters.tex letters/summer-school_participation-letters.tex
	make -C $@

upload: letters csv summer_school/nametags.pdf vouchers dinner_refund.csv
	curl -u $(USER) -T "{$(shell echo letters/*letter*.pdf TUBS_ICCOPT2019*.csv summer_school/nametags.pdf vouchers/vouchers-dinner.pdf | tr ' ' ',')}" https://cloud.wias-berlin.de/aotearoa/remote.php/webdav/ICCOPT2019-documents/ -sw '%{http_code}'

boa/ICCOPT2019_Conference_Book.pdf: xml/db.xml tex
	cd boa; pdflatex ICCOPT2019_boa.tex
	cd boa; pdflatex ICCOPT2019_boa.tex
	cd boa; pdflatex ICCOPT2019_boa.tex
	cd boa; cp ICCOPT2019_boa.pdf ICCOPT2019_Conference_Book.pdf

pdf_files/ICCOPT2019_Parallel_sessions_overview.pdf:
	$(PYTHON) export_first_draft.py

update-schedule: xml/db.xml boa/ICCOPT2019_Conference_Book.pdf pdf_files/ICCOPT2019_Parallel_sessions_overview.pdf xml/schedule.xml webapp
	scp boa/ICCOPT2019_Conference_Book.pdf pdf_files/ICCOPT2019_Parallel_sessions_overview.pdf xml/schedule.xml iccopt2019@spp1962.wias-berlin.de:/srv/www/vhosts/iccopt2019.berlin/downloads/
	rsync -v -e ssh webapp/website/ iccopt2019@spp1962.wias-berlin.de:/srv/www/vhosts/iccopt2019.berlin/conference_app

webapp/website/slots/Mon_1.html: xml/db.xml webapp/templates/*
	$(PYTHON) export_webapp.py

webapp: webapp/website/slots/Mon_1.html

all: xml/schedule.xml tex csv vouchers letters summer_school/nametags.pdf boa/ICCOPT2019_Conference_Book.pdf pdf_files/ICCOPT2019_Parallel_sessions_overview.pdf
