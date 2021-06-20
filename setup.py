from setuptools import find_packages, setup

setup(
    name='django-form-designer-kcs',
    version='1.1.0',
    url='http://github.com/kcsry/django-form-designer',
    license='BSD',
    packages=find_packages('.', include=[
        'form_designer',
        'form_designer.*',
    ]),
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires=[
        'django-picklefield',
    ],
    zip_safe=False,
)
