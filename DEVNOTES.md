# Development Notes


#### Run Tests
```shell
python -m unittest
```

#### Publish to PyPi
```shell
python setup.py sdist
twine upload dist/* --skip-existing
```
