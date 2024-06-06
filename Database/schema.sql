-- creates table for 'foreign' words
CREATE TABLE IF NOT EXISTS "words"(
    "id" INTEGER,
    "name" TEXT NOT NULL UNIQUE,
    PRIMARY KEY("id")
);


-- creates table for word's translations 
CREATE TABLE IF NOT EXISTS "translations"(
    "id" INTEGER,
    "meaning" TEXT NOT NULL UNIQUE,
    PRIMARY KEY("id")
);


-- binding between previous tables.
CREATE TABLE IF NOT EXISTS "translate"(
    "id" INTEGER PRIMARY KEY,
    "word_id" INTEGER,
    "translation_id" INTEGER,
    "example" INTEGER,
    "image" INTEGER,
    "deleted" INTEGER DEFAULT 0,
    UNIQUE ("word_id", "translation_id"),
    FOREIGN KEY("word_id") REFERENCES "words"("id"),
    -- ON DELETE CASCADE,
    FOREIGN KEY("translation_id") REFERENCES "translations"("id")
    -- ON DELETE CASCADE,
);




-- 'foreign' words next to their translation, i.e. dictionary itself
CREATE VIEW IF NOT EXISTS "dictionary" AS 
SELECT "name" AS 'word', "meaning", "example", "image" FROM "words"
LEFT OUTER JOIN "translate" ON "words"."id" = "translate"."word_id"
LEFT OUTER JOIN "translations" ON "translate"."translation_id" = "translations"."id"
WHERE "translate"."deleted" != 1;


-- auto-insert values into all tables only by given word and it's translation 
CREATE TRIGGER IF NOT EXISTS "insert"
INSTEAD OF INSERT ON "dictionary"
FOR EACH ROW 
BEGIN
    --insert word
    INSERT INTO "words"("name")
    VALUES (NEW."word")
    ON CONFLICT ("name") DO NOTHING;
    -- insert meaning
    INSERT INTO "translations"("meaning")
    VALUES (NEW."meaning")
    ON CONFLICT ("meaning") DO NOTHING;

    -- insert bindings
    INSERT INTO "translate"("word_id", "translation_id", "example", "image")
    VALUES ((
        SELECT "id" FROM "words"
        WHERE "name" = (NEW."word")
        ), (
        SELECT "id" FROM "translations"
        WHERE "meaning" = (NEW."meaning")
        ), 
        NEW."example", NEW."image"
    )
    ON CONFLICT ("word_id", "translation_id") DO NOTHING;
END;


-- auto-delete values from all tables by given word and it's translation.
-- This trigger just marks row in "translate" table as deleted.
CREATE TRIGGER IF NOT EXISTS "delete"
INSTEAD OF DELETE ON "dictionary"
FOR EACH ROW 
BEGIN
    UPDATE "translate" SET "deleted" = 1
    WHERE "word_id" = (
        SELECT "id" FROM "words"
        WHERE "name" = (OLD."word")
    ) AND "translation_id" = (
        SELECT "id" FROM "translations"
        WHERE "meaning" = (OLD."meaning")
    );
END;

-- -- auto-delete values from all tables by given word and it's translation.
-- -- This trigger just marks row in "translate" table as deleted.
-- CREATE TRIGGER IF NOT EXISTS "hard_delete"
-- INSTEAD OF DELETE ON "dictionary"
-- FOR EACH ROW 
-- BEGIN
--     DELETE ON "translate"
--     WHERE "word_id" = (
--         SELECT "id" FROM "words"
--         WHERE "name" = (OLD."word")
--     ) AND "translation_id" = (
--         SELECT "id" FROM "translations"
--         WHERE "meaning" = (OLD."meaning")
--     );
-- END;


-- restore values if they were deleted
CREATE TRIGGER IF NOT EXISTS "insert_when_exist"
INSTEAD OF INSERT ON "dictionary"
WHEN NEW."word" IN (
    SELECT "name" FROM "words"
) AND NEW."meaning" IN (
    SELECT "meaning" FROM "translations"
)
BEGIN
    UPDATE "translate" SET "deleted" = 0
    WHERE "word_id" = (
        SELECT "id" FROM "words"
        WHERE "name" = (NEW."word")
    ) AND "translation_id" = (
        SELECT "id" FROM "translations"
        WHERE "meaning" = (NEW."meaning")
    );
END;



CREATE TABLE IF NOT EXISTS "flash_cards"(
    "dictionary_id",
    "word_id" INTEGER,
    "translation_id" INTEGER,
    "example" INTEGER,
    "image" INTEGER,
    "day_added" TEXT,
    "day_learned" TEXT,
    "right_guesses" INTEGER DEFAULT 0,
    "wrong_guesses" INTEGER DEFAULT 0,
    "score" INTEGER DEFAULT 0, 
    "deleted" INTEGER DEFAULT 0,
    "learned" INTEGER DEFAULT 0,
    PRIMARY KEY ("word_id", "translation_id"),
    FOREIGN KEY("word_id") REFERENCES "words"("id"),
    -- ON DELETE CASCADE,
    FOREIGN KEY("translation_id") REFERENCES "translations"("id")
    -- ON DELETE CASCADE,
);
