import { z } from 'zod';

const dateSchema = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}$/)
  .brand<'ApiDate'>();
const positiveIntegerSchema = z.number().int().positive();
const nonNegativeIntegerSchema = z.number().int().nonnegative();

export const SeasonNameSchema = z.enum(['winter', 'spring', 'summer', 'fall']);
export const MatchedFieldNameSchema = z.enum(['name', 'translation', 'aliases']);

export const LatestRatingSchema = z
  .object({
    date: dateSchema,
    score: z.number().finite().nullable(),
    total: nonNegativeIntegerSchema,
    rank: positiveIntegerSchema.nullable(),
  })
  .strict();

export const SeasonSummarySchema = z
  .object({
    year: positiveIntegerSchema,
    season: SeasonNameSchema,
    subject_count: nonNegativeIntegerSchema,
    rated_subject_count: nonNegativeIntegerSchema,
  })
  .strict();

export const SubjectListItemSchema = z
  .object({
    bgm_id: positiveIntegerSchema,
    name: z.string(),
    translation: z.string().nullable(),
    air_date: dateSchema.nullable(),
    year: positiveIntegerSchema.nullable(),
    season: SeasonNameSchema.nullable(),
    tags: z.array(z.string()),
    cover_url: z.string().min(1).nullable(),
    latest_rating: LatestRatingSchema.nullable(),
  })
  .strict();

export const SearchResultItemSchema = SubjectListItemSchema.extend({
  matched_fields: z.array(MatchedFieldNameSchema),
}).strict();

export const SubjectDetailSchema = z
  .object({
    bgm_id: positiveIntegerSchema,
    url: z.string().url(),
    name: z.string(),
    translation: z.string().nullable(),
    aliases: z.array(z.string()),
    summary: z.string().nullable(),
    air_date: dateSchema.nullable(),
    year: positiveIntegerSchema.nullable(),
    season: SeasonNameSchema.nullable(),
    tags: z.array(z.string()),
    cover_url: z.string().min(1).nullable(),
    latest_rating: LatestRatingSchema.nullable(),
  })
  .strict();

export const RatingHistoryPointSchema = LatestRatingSchema;

export const RankingItemSchema = z
  .object({
    position: positiveIntegerSchema,
    metric_value: z.number().finite(),
    subject: SubjectListItemSchema,
  })
  .strict();

export const PaginationSchema = z
  .object({
    page: positiveIntegerSchema,
    page_size: z.number().int().min(1).max(100),
    total: nonNegativeIntegerSchema,
    total_pages: nonNegativeIntegerSchema,
  })
  .strict();

const SubjectPreviewSchema = z.object({ items: z.array(SubjectListItemSchema) }).strict();
const LatestSeasonPreviewSchema = SeasonSummarySchema.extend({
  items: z.array(SubjectListItemSchema),
}).strict();

export const HomeResponseSchema = z
  .object({
    latest_season: LatestSeasonPreviewSchema.nullable(),
    top_score: SubjectPreviewSchema,
    most_rated: SubjectPreviewSchema,
  })
  .strict();

export const SeasonListResponseSchema = z.object({ items: z.array(SeasonSummarySchema) }).strict();

export const SubjectListResponseSchema = z
  .object({
    items: z.array(SubjectListItemSchema),
    pagination: PaginationSchema,
    meta: z
      .object({
        year: positiveIntegerSchema,
        season: SeasonNameSchema,
        min_total: nonNegativeIntegerSchema,
        sort: z.literal('latest_score_desc'),
        snapshot_basis: z.literal('per_subject_latest'),
      })
      .strict(),
  })
  .strict();

export const SearchResponseSchema = z
  .object({
    items: z.array(SearchResultItemSchema),
    pagination: PaginationSchema,
    meta: z
      .object({
        q: z.string(),
        sort: z.literal('match_relevance_then_latest_score_desc'),
      })
      .strict(),
  })
  .strict();

export const TopScoreRankingResponseSchema = z
  .object({
    items: z.array(RankingItemSchema),
    pagination: PaginationSchema,
    meta: z
      .object({
        ranking_type: z.literal('top_score'),
        min_total: nonNegativeIntegerSchema,
        snapshot_basis: z.literal('per_subject_latest'),
      })
      .strict(),
  })
  .strict();

export const MostRatedRankingResponseSchema = z
  .object({
    items: z.array(RankingItemSchema),
    pagination: PaginationSchema,
    meta: z
      .object({
        ranking_type: z.literal('most_rated'),
        snapshot_basis: z.literal('per_subject_latest'),
      })
      .strict(),
  })
  .strict();

export const RatingHistoryResponseSchema = z
  .object({
    bgm_id: positiveIntegerSchema,
    available_range: z.object({ from: dateSchema, to: dateSchema }).strict().nullable(),
    items: z.array(RatingHistoryPointSchema),
  })
  .strict();

export const ApiErrorResponseSchema = z
  .object({
    error: z.object({ code: z.string(), message: z.string() }).strict(),
  })
  .strict();

export type ApiDate = z.infer<typeof dateSchema>;
export type SeasonName = z.infer<typeof SeasonNameSchema>;
export type MatchedFieldName = z.infer<typeof MatchedFieldNameSchema>;
export type LatestRating = z.infer<typeof LatestRatingSchema>;
export type SeasonSummary = z.infer<typeof SeasonSummarySchema>;
export type SubjectListItem = z.infer<typeof SubjectListItemSchema>;
export type SearchResultItem = z.infer<typeof SearchResultItemSchema>;
export type SubjectDetail = z.infer<typeof SubjectDetailSchema>;
export type RatingHistoryPoint = z.infer<typeof RatingHistoryPointSchema>;
export type RankingItem = z.infer<typeof RankingItemSchema>;
export type Pagination = z.infer<typeof PaginationSchema>;
export type HomeResponse = z.infer<typeof HomeResponseSchema>;
export type SeasonListResponse = z.infer<typeof SeasonListResponseSchema>;
export type SubjectListResponse = z.infer<typeof SubjectListResponseSchema>;
export type SearchResponse = z.infer<typeof SearchResponseSchema>;
export type TopScoreRankingResponse = z.infer<typeof TopScoreRankingResponseSchema>;
export type MostRatedRankingResponse = z.infer<typeof MostRatedRankingResponseSchema>;
export type RatingHistoryResponse = z.infer<typeof RatingHistoryResponseSchema>;
export type ApiErrorResponse = z.infer<typeof ApiErrorResponseSchema>;
