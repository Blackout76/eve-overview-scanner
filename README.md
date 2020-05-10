# eve_trafic_analyser_sofware


## Requests

#### Example of request 1: All jump using specific ship, war eligible and specific system
```
SELECT jump_on,
	P.name AS pilot, 
	S.type_name AS ship,
    S1.solarsystem_name AS system_from, 
    S2.solarsystem_name AS system_to,
    P.corporation_name AS corporation,
    P.alliance_name AS alliance
    FROM jump J
JOIN solarsystem S1 on S1.solarsystem_id = J.system_from_id
JOIN solarsystem S2 on S2.solarsystem_id = J.system_to_id
JOIN pilot P on P.id = J.pilot_id
JOIN ship S ON S.type_id = J.ship_id
WHERE 
	P.war_eligible IS TRUE
AND S2.solarsystem_name = 'Jita'
AND S.type_name IN ('Providence','Charon','Obelisk','Fenrir','Ark','Rhea','Anshar','Nomad')
```

#### Example of request 2: Get all alliance and corporation jumps sorted by count with war elegible in a specific system
```
SELECT Count(),
    S2.solarsystem_name AS system_to,
    P.corporation_name AS corporation,
    P.alliance_name AS alliance
    FROM jump J
JOIN solarsystem S2 on S2.solarsystem_id = J.system_to_id
JOIN pilot P on P.id = J.pilot_id
WHERE 
	P.war_eligible IS TRUE
AND S2.solarsystem_name = 'Jita'
GRoup BY P.corporation_id, P.alliance_id
ORDER BY COUNT(*) DESC
```
