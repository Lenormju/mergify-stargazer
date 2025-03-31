import pytest
from fastapi.testclient import TestClient

from stargazer_api import app, AUTHORIZED_LOGIN, AUTHORIZED_PASSWORD, _init_core



@pytest.fixture(scope="module")
def test_client() -> TestClient:
    _init_core()  # TODO: find how to integrate with lifespan
    return TestClient(app)


def test__flaky__starneighbours_lenormj_talk_and_cfp(test_client: TestClient) -> None:
    response = test_client.get("/repos/Lenormju/talk-et-cfp/starneighbours",
                               auth=(AUTHORIZED_LOGIN, AUTHORIZED_PASSWORD))
    assert response.status_code == 200
    # TODO: find how to have a non-flaky test, i.e. create some test users and repos ?
    assert response.json() == [{'repo': 'AntonyCanut/AntonyCanut', 'stargazers': ['rod2j']},
                               {'repo': 'Devskiller/friendly-id', 'stargazers': ['rod2j']},
                               {'repo': 'JMHReif/pouring-coffee-into-matrix-lombok', 'stargazers': ['rod2j']},
                               {'repo': 'LawrenceDLockhart/vaadin-combo-app', 'stargazers': ['rod2j']},
                               {'repo': 'Netflix/concurrency-limits', 'stargazers': ['rod2j']},
                               {'repo': 'Netflix/conductor', 'stargazers': ['rod2j']},
                               {'repo': 'Pierrotws/kafka-ssl-compose', 'stargazers': ['rod2j']},
                               {'repo': 'VaughnVernon/IDDD_NYSE', 'stargazers': ['rod2j']},
                               {'repo': 'VaughnVernon/IDDD_Samples', 'stargazers': ['rod2j']},
                               {'repo': 'VaughnVernon/ReactiveMessagingPatterns_ActorModel', 'stargazers': ['rod2j']},
                               {'repo': 'amalnev/declarative-nats-listeners', 'stargazers': ['rod2j']},
                               {'repo': 'asyncapi/modelina', 'stargazers': ['rod2j']},
                               {'repo': 'asyncapi/spec', 'stargazers': ['rod2j']},
                               {'repo': 'boyney123/awesome-event-patterns', 'stargazers': ['rod2j']},
                               {'repo': 'cowtowncoder/java-uuid-generator', 'stargazers': ['rod2j']},
                               {'repo': 'dilgerma/eventsourcing-book', 'stargazers': ['rod2j']},
                               {'repo': 'eclipse-ee4j/cargotracker', 'stargazers': ['rod2j']},
                               {'repo': 'emqx/emqx', 'stargazers': ['rod2j']},
                               {'repo': 'eugene-khyst/postgresql-event-sourcing', 'stargazers': ['rod2j']},
                               {'repo': 'failsafe-lib/failsafe', 'stargazers': ['rod2j']},
                               {'repo': 'fraktalio/fmodel', 'stargazers': ['rod2j']},
                               {'repo': 'fraktalio/fmodel-java', 'stargazers': ['rod2j']},
                               {'repo': 'fraktalio/fstore-sql', 'stargazers': ['rod2j']},
                               {'repo': 'google/CallBuilder', 'stargazers': ['rod2j']},
                               {'repo': 'helidon-io/helidon', 'stargazers': ['rod2j']},
                               {'repo': 'hibernate/hibernate-reactive', 'stargazers': ['rod2j']},
                               {'repo': 'hivemq/hivemq-azure-cluster-discovery-extension', 'stargazers': ['rod2j']},
                               {'repo': 'hivemq/hivemq-community-edition', 'stargazers': ['rod2j']},
                               {'repo': 'hivemq/hivemq-mqtt-client', 'stargazers': ['rod2j']},
                               {'repo': 'jenkinsci/config-driven-pipeline-plugin', 'stargazers': ['rod2j']},
                               {'repo': 'jupiter-tools/spring-test-kafka', 'stargazers': ['rod2j']},
                               {'repo': 'mbhave/tdd-with-spring-boot', 'stargazers': ['rod2j']},
                               {'repo': 'mvpjava/docker-spring-sts4-ide', 'stargazers': ['rod2j']},
                               {'repo': 'mvpjava/springboot-IntegrationTests-Tutorial', 'stargazers': ['rod2j']},
                               {'repo': 'mvpjava/springboot-JUnit5-tutorial', 'stargazers': ['rod2j']},
                               {'repo': 'nicolaferraro/camel-saga-quickstart', 'stargazers': ['rod2j']},
                               {'repo': 'openfga/community', 'stargazers': ['rod2j']},
                               {'repo': 'openfga/frontend-utils', 'stargazers': ['rod2j']},
                               {'repo': 'openfga/openfga', 'stargazers': ['rod2j']},
                               {'repo': 'openfga/roadmap', 'stargazers': ['rod2j']},
                               {'repo': 'openfga/sdk-generator', 'stargazers': ['rod2j']},
                               {'repo': 'permitio/OPToggles', 'stargazers': ['rod2j']},
                               {'repo': 'permitio/opal', 'stargazers': ['rod2j']},
                               {'repo': 'piranhacloud/piranha', 'stargazers': ['rod2j']},
                               {'repo': 'quarkusio/quarkus', 'stargazers': ['rod2j']},
                               {'repo': 'redhat-italy/rht-summit2019-saga', 'stargazers': ['rod2j']},
                               {'repo': 'rod2j/data-jdbc-issue-551', 'stargazers': ['rod2j']},
                               {'repo': 'rod2j/parallel-consumer', 'stargazers': ['rod2j']},
                               {'repo': 'rod2j/spring-kafka', 'stargazers': ['rod2j']},
                               {'repo': 'salesforce/centrifuge', 'stargazers': ['rod2j']},
                               {'repo': 'salesforce/kafka-junit', 'stargazers': ['rod2j']},
                               {'repo': 'salesforce/kafka-partition-availability-benchmark', 'stargazers': ['rod2j']},
                               {'repo': 'salesforce/mirus', 'stargazers': ['rod2j']},
                               {'repo': 'salesforce/rules_spring', 'stargazers': ['rod2j']},
                               {'repo': 'spring-cloud/spring-cloud-stream', 'stargazers': ['rod2j']},
                               {'repo': 'spring-projects/spring-data-relational', 'stargazers': ['rod2j']},
                               {'repo': 'spring-projects/spring-kafka', 'stargazers': ['rod2j']},
                               {'repo': 'vlingo/xoom-actors', 'stargazers': ['rod2j']},
                               {'repo': 'vlingo/xoom-examples', 'stargazers': ['rod2j']},
                               {'repo': 'wiverson/htmx-demo', 'stargazers': ['rod2j']},
                               {'repo': 'xmolecules/jmolecules', 'stargazers': ['rod2j']},
                               {'repo': 'zalando/jackson-datatype-money', 'stargazers': ['rod2j']},
                               {'repo': 'zalando/problem', 'stargazers': ['rod2j']},
                               {'repo': 'zalando/problem-spring-web', 'stargazers': ['rod2j']},
                               {'repo': 'zalando/restful-api-guidelines', 'stargazers': ['rod2j']},
                               {'repo': 'zenika-open-source/zenika-process', 'stargazers': ['rod2j']}]
