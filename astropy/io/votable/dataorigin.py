# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""Extract Data Origin in VOTable.

References
----------
DataOrigin is a vocabulary described in the IVOA note: https://www.ivoa.net/documents/DataOrigin/

Notes
-----
This API retrieve Metadata from INFO in VOTable.
The information can be found at different level in a VOTable:

- global level
- resource level
- table level

Contents
--------

- Query information: Each element is considered to be unique in the VOTable.
  Information concerns publisher, date of execution, contact, request, etc.
- Dataset origin : basic provenance information.

Examples
--------
For more information, please see :ref:`DataOrigin documentation <astropy-io-votable-dataorigin>`.
"""

import astropy.io.votable.tree

__all__ = [
    "DataOrigin",
    "DatasetOrigin",
    "QueryOrigin",
    "add_data_origin_info",
    "extract_data_origin",
]


DATAORIGIN_QUERY_INFO = (
    "service_ivoid",
    "publisher",
    "server_software",
    "service_protocol",
    "request",
    "query",
    "request_date",
    "contact",
)


DATAORIGIN_INFO = (
    "data_ivoid",
    "citation",
    "reference_url",
    "resource_version",
    "rights_uri",
    "rights",
    "creator",
    "journal",
    "article",
    "cites",
    "is_derived_from",
    "original_date",
    "publication_date",
    "last_update_date",
)


class QueryOrigin:
    """Data class storing query execution information that generated the VOTable.

    Notes
    -----
    The Query information should be unique in the whole VOTable.
    It includes reproducibility information to execute the query again.

    Attributes
    ----------
    service_ivoid : str
        IVOID of the service that produced the VOTable (default: None)

    publisher : str
        Data centre that produced the VOTable (default: None)

    server_software : str
        Software version (default: None)

    service_protocol : str
        IVOID of the protocol through which the data was retrieved (default: None)

    request : str
        Full request URL including a query string (default: None)

    query : str
        An input query in a formal language (e.g, ADQL) (default: None)

    request_date : str
        Query execution date (default: None)

    contact : str
        Email or URL to contact publisher (default: None)

    infos : list[astropy.io.votable.tree.Info]
        list of ``<INFO>`` used by DataOrigin (default: empty list)

    """

    def __init__(self, votable_element: astropy.io.votable.tree.Element = None):
        self.service_ivoid = None
        self.publisher = None
        self.server_software = None
        self.service_protocol = None
        self.request = None
        self.query = None
        self.request_date = None
        self.contact = None
        self.infos = []

    def __str__(self) -> str:
        s = []
        for info_name in DATAORIGIN_QUERY_INFO:
            info = getattr(self, info_name)
            if info:
                s.append(f"{info_name}: {info}")
        return "\n".join(s)


class DatasetOrigin:
    """Data class storing the basic provenance for a Dataset.

    Notes
    -----
    DatasetOrigin is dedicated to a specific Element in a VOTable.
    These ``<INFO>`` Elements describe a Resource, a TableElement or are Global.

    Attributes
    ----------
    data_ivoid : list
        IVOID of underlying data collection (default: None)

    citation : list
        Dataset identifier that can be used for citation (default: None)

    reference_url : list
        Dataset landing page (default: None)

    resource_version : list
        Dataset version (default: None)

    rights_uri : list
        Licence URI (default: None)

    rights : list
        Licence or Copyright text (default: None)

    creator : list
        The person(s) mainly involved in the creation of the resource (default: None)

    journal : list
        Editor name of the reference article (default: None)

    article : list
        Bibcode or DOI of a reference article (default: None)

    cites : list
        An Identifier (ivoid, DOI, bibcode) of second resource (default: None)

    is_derived_from : list
        An Identifier (ivoid, DOI, bibcode) of second resource (default: None)

    original_date : list
        Date of the original resource from which the present resource is derived (default: None)

    publication_date : list
        Date of first publication in the data centre (default: None)

    last_update_date : list
        Last data centre update (default: None)

    infos : list[astropy.io.votable.tree.Info]
        list of ``<INFO>`` used by DataOrigin (default: None)
    """

    def __init__(self, votable_element: astropy.io.votable.tree.Element = None):
        """
        Constructor

        Parameters
        ----------
        votable_element: astropy.io.votable.tree.Element, optional
                         indicates the VOTable element
        """
        self.ivoid = None
        self.citation = None
        self.reference_url = None
        self.resource_version = None
        self.rights_uri = None
        self.rights = None
        self.creator = None
        self.editor = None
        self.article = None
        self.cites = None
        self.is_derived_from = None
        self.original_date = None
        self.publication_date = None
        self.last_update_date = None
        self.__vo_elt = votable_element
        self.infos = []

    @property
    def ivoid(self) -> str:
        """Compatibility with previous version"""
        return self.data_ivoid

    @ivoid.setter
    def ivoid(self, value: str):
        """Compatibility with previous version"""
        self.data_ivoid = value

    @property
    def editor(self) -> str:
        """Compatibility with previous version"""
        return self.journal

    @editor.setter
    def editor(self, value: str):
        """Compatibility with previous version"""
        self.journal = value

    def get_votable_element(self) -> astropy.io.votable.tree.Element:
        """
        Get the VOTable element

        Returns
        -------
        astropy.io.votable.tree.Element
        """
        return self.__vo_elt

    def __str__(self) -> str:
        s = []
        for info_name in DATAORIGIN_INFO:
            info = getattr(self, info_name)
            if info:
                s.append(f"{info_name}: {','.join(info)}")
        return "\n".join(s)


class DataOriginContainer:
    """Data class storing both information about query execution
       and basic provenances of datasets used to generate the VOTable.

    Attributes
    ----------
    query : QueryOrigin
        request information (default: None)

    origin : list[DatasetOrigin]
        list of DatasetOrigin (default: empty)

    Notes
    -----
    The class includes an iterator on Attribute origin.
    """

    def __init__(self):
        self.query = QueryOrigin()
        self.origin = []
        self.__it = None

    def __str__(self) -> str:
        origin_list = []
        for origin in self.origin:
            origin_list.append(str(origin))
        return str(self.query) + "\n\n" + "\n\n".join(origin_list)

    def __iter__(self):
        self.__it = -1
        return self

    def __next__(self):
        self.__it += 1
        if self.__it >= len(self.origin):
            raise StopIteration
        return self.origin[self.__it]


class DataOrigin(DataOriginContainer):
    """Class parsing a VOTable and storing both information about query execution
    and basic provenances.
    The class is derived from DataOriginContainer.
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    def __empty_dataset_origin(o: DatasetOrigin) -> bool:
        """(internal) check if DataOrigin is filled"""
        for info in DATAORIGIN_INFO:
            v = getattr(o, info)
            if v is not None:
                return False
        return True

    def __extract_generic_info(
        self, vo_element: astropy.io.votable.tree.Element, infos: list
    ):
        """(internal) extract info and populate DataOrigin

        Parameters
        ----------
        vo_element : astropy.io.votable.tree.Element
            VOTable element (votable, resource or table)

        infos : list[astropy.io.votable.tree.Info]
            list of ``<INFO>``

        """
        if not infos:
            return

        dataset_origin = DatasetOrigin(vo_element)

        for info in infos:
            info_name = info.name.lower()
            for dataorigin_info in DATAORIGIN_INFO:
                if info_name == dataorigin_info:
                    dataset_origin.infos.append(info)
                    att = getattr(dataset_origin, dataorigin_info)
                    if att is None:
                        setattr(dataset_origin, dataorigin_info, [info.value])
                    else:
                        att.append(info.value)
                    break

            for query_info in DATAORIGIN_QUERY_INFO:
                if info_name == query_info:
                    self.query.infos.append(info)
                    setattr(self.query, query_info, info.value)
                    break

        if not DataOrigin.__empty_dataset_origin(dataset_origin):
            self.origin.append(dataset_origin)

    def __extract_dali_info(self, infos: list):
        """(internal) append with DALI INFO

        Parameters
        ----------
        infos : list[astropy.io.votable.tree.Info]
            iterable info.
        """
        if not self.query.service_protocol:
            for info in infos:
                info_name = info.name.lower()
                if info_name == "standardid":
                    if not self.query.service_protocol:
                        if self.info is None:
                            self.infos = []
                        self.quey.infos.append(info)
                        self.query.service_protocol = info.value

    def __extract_info_from_table(self, table: astropy.io.votable.tree.TableElement):
        """(internal) extract and populate dataOrigin from astropy.io.votable.tree.TableElement

        Parameters
        ----------
        table : astropy.io.votable.tree.TableElement
            Table to explore.
        """
        self.__extract_generic_info(table, table.infos)

    def __extract_info_from_resource(
        self,
        resource: astropy.io.votable.tree.Resource,
        recursive: bool = True,
    ):
        """(internal) extract and populate dataOrigin from astropy.io.votable.tree.Resource

        Parameters
        ----------
        param resource : astropy.io.votable.tree.Resource
            Resource to explore.

        recursive : bool, optional
            make a recursive search (default: True)
        """
        self.__extract_generic_info(resource, resource.infos)
        self.__extract_dali_info(resource.infos)
        if recursive:
            for table in resource.tables:
                self.__extract_info_from_table(table)

    def __extract_info_from_votable(
        self,
        votable: astropy.io.votable.tree.VOTableFile,
        recursive: bool = True,
    ):
        """(internal) extract and populate dataOrigin from astropy.io.votable.tree.VOTableFile

        Parameters
        ----------
        votable : astropy.io.votable.tree.VOTableFile
            VOTableFile to explore.

        recursive : bool, optional
            make a recursive search (default: True)
        """
        self.__extract_generic_info(votable, votable.infos)
        if recursive:
            for resource in votable.resources:
                self.__extract_info_from_resource(resource)

    def parse(self, vot_element: astropy.io.votable.tree.Element) -> None:
        """Extract DataOrigin in a VO element

        Parameters
        ----------
        vot_element : astropy.io.votable.tree.Info
            VOTable Element to explore

        Raises
        ------
        TypeError
            input ``vot_element`` type is not supported
        """
        if isinstance(vot_element, astropy.io.votable.tree.VOTableFile):
            self.__extract_info_from_votable(vot_element)
        elif isinstance(vot_element, astropy.io.votable.tree.Resource):
            self.__extract_info_from_resource(vot_element)
        elif isinstance(vot_element, astropy.io.votable.tree.TableElement):
            self.__extract_info_from_table(vot_element)
        else:
            raise TypeError("input vot_element type is not supported.")


class DataOriginWriter(DataOrigin):
    """Class to update a VOTable with DataOrigin.
    The class derived from DataOrigin.
    """

    def __init__(self):
        super().__init__()
        self.__vo_elt = None

    def parse(self, vot_element: astropy.io.votable.tree.Element) -> None:
        """Extract DataOrigin in a VO element

        Parameters
        ----------
        vot_element : astropy.io.votable.tree.Info
            VOTable Element to explore

        Raises
        ------
        TypeError
            input ``vot_element`` type is not supported
        """
        super().parse(vot_element)
        self.__vo_elt = vot_element

    @staticmethod
    def __clean_votable_info(vot_element: astropy.io.votable.tree.Element) -> None:
        """(internal) Clean existing DataOrigin INFO in the VOTable Element

        Parameters
        ----------
        vot_element : astropy.io.votable.tree.Element
            VOTable Element where to remove the INFO

        """
        for info in vot_element.infos:
            vot_element.infos.remove(info)

        if isinstance(vot_element, astropy.io.votable.tree.Resource):
            for table in vot_element.resources:
                DataOriginWriter.__clean_votable_info(table)
        elif isinstance(vot_element, astropy.io.votable.tree.VOTableFile):
            for resource in vot_element.resources:
                DataOriginWriter.__clean_votable_info(resource)

    @staticmethod
    def __append_votable_info(
        vot_element: astropy.io.votable.tree.Element,
        name: str,
        value: str | list,
        content: str | None,
        unique: bool = False,
    ) -> None:
        """(internal) add new DATAOrigin info in the VOTable Element

        Parameters
        ----------
        vot_element : astropy.io.votable.tree.Element
            VOTable Element where to add a new INFO

        name : str
            INFO name

        value: str | list
            the INFO value

        content: str, optional
            INFO description (default: None)

        unique: bool, optional
            the INFO element is unique (default: False)

        """
        if not isinstance(
            vot_element,
            (
                astropy.io.votable.tree.VOTableFile,
                astropy.io.votable.tree.Resource,
                astropy.io.votable.tree.TableElement,
            ),
        ):
            raise TypeError("input vot_element type is not supported.")

        for info in vot_element.infos:
            if info.name == name:
                if unique:
                    return
                if info.value == value:
                    return

        values = [value] if not isinstance(value, list) else value
        for val in values:
            new_info = astropy.io.votable.tree.Info(name=name, value=val)
            if content:
                new_info.content = content
            vot_element.infos.extend([new_info])

    def update_votable(self) -> astropy.io.votable.tree.Element:
        """Update the votable with DataOrigin

        Returns
        -------
        astropy.io.votable.tree.Element

        """
        if self.__vo_elt is None:
            raise ValueError("empty votable")

        # clean existing DataOrigin info
        DataOriginWriter.__clean_votable_info(self.__vo_elt)

        for item in DATAORIGIN_QUERY_INFO:
            att = getattr(self.query, item)
            if not att:
                continue

            DataOriginWriter.__append_votable_info(
                self.__vo_elt, name=item, value=att, unique=True
            )

        for origin_info in self.origin:
            for item in DATAORIGIN_INFO:
                att = getattr(origin_info, item)
                if not att:
                    continue

                vo_elt = origin_info.get_votable_element()
                if not vo_elt:
                    vo_elt = self.__vo_elt
                DataOriginWriter.__append_votable_info(vo_elt, name=item, value=att)

        return self.__vo_elt


def extract_data_origin(vot_element: astropy.io.votable.tree.Element) -> DataOrigin:
    """Extract DataOrigin in a VO element

    Parameters
    ----------
    vot_element : astropy.io.votable.tree.Info
        VOTable Element to explore

    Returns
    -------
    DataOrigin

    Raises
    ------
    TypeError
        input ``vot_element`` type is not supported
    """
    data_origin = DataOrigin()
    data_origin.parse(vot_element)
    return data_origin


def add_data_origin_info(
    vot_element: astropy.io.votable.tree.Element,
    info_name: str,
    info_value: str,
    content: str | None = None,
) -> None:
    """Update VOTable element with information compatible
       with DataOrigin vocabulary.

    Notes
    -----
    The function checks information name and adds the
    VOTable element with a new ``<INFO>``.

    Parameters
    ----------
    vot_element : astropy.io.votable.tree.Element
        VOTable element where to add the information

    info_name : str
        Attribute name (see DATAORIGIN_INFO, DATAORIGIN_QUERY_INFO)

    info_value : str
        value

    content : str, optional
        Content in ``<INFO>`` (default: None)

    Raises
    ------
    TypeError
        input type not managed or information name not recognized
    ValueError
        ``info_name`` already exists in ``vot_element``
    ValueError
        ``info_name`` is an unknown DataOrigin name.
    """
    if info_name in DATAORIGIN_INFO:
        if not isinstance(
            vot_element,
            (
                astropy.io.votable.tree.VOTableFile,
                astropy.io.votable.tree.Resource,
                astropy.io.votable.tree.TableElement,
            ),
        ):
            raise TypeError("Unsupported vot_element type.")

    elif info_name in DATAORIGIN_QUERY_INFO:
        if not isinstance(vot_element, astropy.io.votable.tree.VOTableFile):
            raise TypeError(
                "Bad type of vot_element: this information needs VOTableFile."
            )

        for info in vot_element.get_infos_by_name(info_name):
            raise ValueError(f"QueryOrigin {info_name} already exists")

    else:
        raise ValueError("Unknown DataOrigin info name.")

    new_info = astropy.io.votable.tree.Info(name=info_name, value=info_value)
    if content:
        new_info.content = content
    vot_element.infos.extend([new_info])
