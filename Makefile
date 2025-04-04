# Copyright 2022, Robert Dyer, Samuel W. Flint,
#                 and University of Nebraska Board of Regents
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

PYTHON:=python3
VERBOSE:=

ZIP:=zip
ZIPOPTIONS:=-u -r
ZIPIGNORES:=-x \*/.DS_Store -x \*/.gitkeep -x data/csv/\*


.PHONY: all
all: analysis

include Makefile.study

Makefile.study: study-config.json bin/build-makefile.py
	jsonschema --instance study-config.json schemas/0.1.2/study-config.schema.json
	$(PYTHON) bin/build-makefile.py > $@

update-figures:
	cd paper ; git pull ; rm -Rf figures/ tables/ ; cp -R ../figures . ; cp -R ../tables . ; git add -f figures/ tables/ ; git commit -m 'update figures/tables' ; git push


####################
# packaging targets
#
.PHONY: package zip
zip: package
package:
	-$(ZIP) replication-pkg.zip $(ZIPOPTIONS) .vscode/*.json analyses/**/*.py analyses/*.py bin/**/*.py bin/*.py data/*.xlsx boa/ figures/ schemas/ tables/ jobs.json LICENSE Makefile README.md requirements.txt CODEBOOK.md study-config.json $(ZIPIGNORES)
	-$(ZIP) data.zip $(ZIPOPTIONS) data/txt/ $(ZIPIGNORES)
	-$(ZIP) data-cache.zip $(ZIPOPTIONS) data/parquet/ $(ZIPIGNORES)

.PHONY: docker run-docker
docker:
	@cp -f requirements.txt requirements.txt.save
	@sed 's/>=/==/g' requirements.txt.save > requirements.txt
	docker build -t kotlin-inference:latest .
	@cp -f requirements.txt.save requirements.txt
	@$(RM) requirements.txt.save

run-docker: docker
	docker run -it -v $(shell pwd):/study kotlin-inference:latest


################
# clean targets
#
.PHONY: clean clean-data clean-csv clean-pq clean-txt clean-zip clean-all

clean:
	rm -Rf __pycache__ bin/__pycache__
	rm -f figures/**/*.pdf figures/*.pdf
	rm -f tables/**/*.tex tables/*.tex

clean-data: clean-csv clean-pq clean-txt

clean-csv:
	rm -f data/csv/**/*.csv data/csv/*.csv

clean-pq:
	rm -f data/parquet/**/*.parquet data/parquet/*.parquet

clean-txt:
	rm -f data/txt/**/*.txt data/txt/*.txt

clean-zip:
	rm -f replication-pkg.zip data.zip data-cache.zip

clean-all: clean clean-data clean-zip
