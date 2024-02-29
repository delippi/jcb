<div
  align="center"
>

<img
  style="vertical-align:middle"
  src="https://github.com/danholdaway/jcb/blob/develop/etc/jcb.png"
  width="30%"
  alt="JEDI Configuration Builder"
/>

<img
  style="vertical-align:middle"
  src="https://github.com/danholdaway/jcb/blob/develop/etc/jcb-text.png"
  width="40%"
  alt="JEDI Configuration Builder"
/>
</div>

#

### Licence:

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

### Installation

``` shell
git clone https://github.com/noaa-emc/jcb
cd jcb
pip install --prefix=/path/to/where/you/want/installed .
```

### Description

How to use from the command line:

``` shell
jcb render dictionary_of_templates.yaml jedi_config.yaml
```

The below shows two examples of calling jcb from a python client. In each case you have to provide a dictionary that describes all the ways that you want to render the templates in the contained JEDI YAML files.

First jcb provides a convenient single line call passing in the dictionary of templated and getting back the dictionary. The dictionary of templates has to contain an `algorithm` key telling the system which JEDI algorithm you want to run.

``` python
import jcb

jedi_config_dict = jcb.render(dictionary_of_templates)
```

For situations where you wish to create YAML files for several algorithms using the same dictionary of templates you can access the class directly.

``` python
import jcb

jcb_obj = jcb.Renderer(dictionary_of_templates)
jedi_dict_2_a = jcb_obj.render('hofx4d')
jedi_dict_2_b = jcb_obj.render('variational')
```
