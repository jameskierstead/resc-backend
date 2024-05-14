# Standard Library
import logging

# Third Party
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

# First Party
from resc_backend.db.model import DBrule, DBruleAllowList, DBrulePack, DBscan
from resc_backend.resc_web_service.schema import (
    rule_allow_list as rule_allow_list_schema,
)
from resc_backend.resc_web_service.schema.rule import RuleCreate, RuleRead

logger = logging.getLogger(__name__)


def get_rules_by_scan_id(db_connection: Session, scan_id: int) -> list[RuleRead]:
    """
        Get rules by scan id
    :param db_connection:
        Session of the database connection
    :param scan_id:
        scan id for which rules need to be fetched
    :return: List[RuleRead]
        The output contains list of rules
    """
    rule_query = db_connection.query(DBrule)
    rule_query = rule_query.join(DBscan, DBscan.rule_pack == DBrule.rule_pack)
    rule_query = rule_query.where(DBscan.id_ == scan_id)
    rules: list[RuleRead] = rule_query.all()
    return rules


def create_rule_allow_list(db_connection: Session, rule_allow_list: rule_allow_list_schema.RuleAllowList):
    """
        Create rule allow list in database
    :param db_connection:
        Session of the database connection
    :param rule_allow_list:
        RuleAllowList object to be created
    """
    db_rule_allow_list = DBruleAllowList(
        description=rule_allow_list.description,
        regexes=rule_allow_list.regexes,
        paths=rule_allow_list.paths,
        commits=rule_allow_list.commits,
        stop_words=rule_allow_list.stop_words,
    )
    db_connection.add(db_rule_allow_list)
    db_connection.commit()
    db_connection.refresh(db_rule_allow_list)
    return db_rule_allow_list


def create_rule(db_connection: Session, rule: RuleCreate):
    """
        Create rule in database
    :param db_connection:
        Session of the database connection
    :param rule:
        RuleCreate object to be created
    """
    db_rule = DBrule(
        rule_name=rule.rule_name,
        description=rule.description,
        entropy=rule.entropy,
        secret_group=rule.secret_group,
        regex=rule.regex,
        path=rule.path,
        keywords=rule.keywords,
        rule_pack=rule.rule_pack,
        allow_list=rule.allow_list,
    )
    db_connection.add(db_rule)
    db_connection.commit()
    db_connection.refresh(db_rule)
    return db_rule


def get_rules_by_rule_pack_version(db_connection: Session, rule_pack_version: str) -> list[str]:
    """
        Fetch rules by rule pack version
    :param db_connection:
        Session of the database connection
    :param rule_pack_version:
        rule pack version
    :return: List[str]
        The output contains list of strings of global allow list
    """
    query: Query = db_connection.query(
        DBrule.id_,
        DBrule.rule_pack,
        DBrule.rule_name,
        DBrule.entropy,
        DBrule.secret_group,
        DBrule.regex,
        DBrule.path,
        DBrule.keywords,
        DBruleAllowList.description,
        DBruleAllowList.regexes,
        DBruleAllowList.paths,
        DBruleAllowList.commits,
        DBruleAllowList.stop_words,
    )

    query = query.join(DBrulePack, DBrulePack.version == DBrule.rule_pack)
    query = query.join(DBruleAllowList, DBruleAllowList.id_ == DBrule.allow_list, isouter=True)
    query = query.where(DBrule.rule_pack == rule_pack_version)
    query = query.order_by(DBrule.id_)
    db_rules = query.all()

    return db_rules


def get_global_allow_list_by_rule_pack_version(db_connection: Session, rule_pack_version: str) -> list[str]:
    """
        Retrieve global allow list by rule pack version
    :param db_connection:
        Session of the database connection
    :param rule_pack_version:
        rule pack version
    :return: List[str]
        The output contains list of strings of global allow list
    """
    query: Query = db_connection.query(
        DBrulePack.version,
        DBruleAllowList.description,
        DBruleAllowList.regexes,
        DBruleAllowList.paths,
        DBruleAllowList.commits,
        DBruleAllowList.stop_words,
    )
    query = query.join(DBruleAllowList, DBruleAllowList.id_ == DBrulePack.global_allow_list)
    query = query.where(DBrulePack.version == rule_pack_version)
    query = query.order_by(DBruleAllowList.id_)
    db_global_allow_list = query.first()

    return db_global_allow_list
