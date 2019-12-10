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

xml/db.xml: converia-input/build_xml_db.py converia-input/paper.xml converia-input/EVENT_Agenda.csv converia-input/EVENT_Personenliste.csv converia-input/log.csv converia-input/free_participation.csv converia-input/late_summer_school.csv converia-input/late_dinner.csv
	cd converia-input; $(PYTHON) build_xml_db.py

xml/schedule.xml: xml/db.xml build_schedule.py
	$(PYTHON) build_schedule.py

csv: xml/db.xml other/build_tubs_list.py
	cd other; $(PYTHON) build_tubs_list.py

vouchers: xml/db.xml
	$(PYTHON) export_dinner_tickets.py
	$(PYTHON) export_vouchers.py
	make -C $@

letters/ICCOPT2019_participation-letters.tex: xml/db.xml export_participation_letters.py
	$(PYTHON) export_participation_letters.py

letters/summer-school_participation-letters.tex: xml/db.xml export_summerschool_letters.py
	$(PYTHON) export_summerschool_letters.py

summer_school/summer-school-participants.tex: xml/db.xml build_summer_school_nametags.py
	$(PYTHON) build_summer_school_nametags.py

summer_school/nametags.pdf: summer_school/nametags.tex summer_school/summer-school-participants.tex
	make -C summer_school

letters: letters/ICCOPT2019_participation-letters.tex letters/summer-school_participation-letters.tex
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