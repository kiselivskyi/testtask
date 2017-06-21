from setuptools import setup

requires = [
    'pyramid',
    'pyramid_chameleon',
    'deform',
	'pyramid_mailer'
]

setup(name='tutorial',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = tutorial:main
      """,
)