class Queries:

    get_last_encounter = """
    query ($char_realm: String!, $char_name: String!, $char_server: String!) {
  rateLimitData {
    limitPerHour
    pointsSpentThisHour
    pointsResetIn
  }
  characterData {
    character(name: $char_name, serverSlug: $char_realm, serverRegion: $char_server) {
      name
      id
      classID
      recentReports(limit: 1) {
        data {
          fights(killType: Encounters) {
            encounterID
            name
            endTime
          }
        }
      }
    }
  }
}
"""

    get_gear = """
    query($char_realm: String!, $char_name: String!, $char_server: String!, $encounter: Int!) {
  rateLimitData {
    limitPerHour
    pointsSpentThisHour
    pointsResetIn
  }
  characterData {
    character(name: $char_name, serverSlug: $char_realm, serverRegion: $char_server) {
      name
      id
      classID
      encounterRankings(includeCombatantInfo: true, byBracket: true, encounterID: $encounter)
    }
  }
}
"""

    check_bearer = """
    query {
  rateLimitData {
    limitPerHour
    pointsSpentThisHour
    pointsResetIn
  }
}
"""
