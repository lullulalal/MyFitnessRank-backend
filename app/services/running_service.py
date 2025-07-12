import math

from typing import List
from ..schemas.running_schema import RunningRequest, RunningResponse, HistogramResult, HistogramBin
from ..models.running_model import RunningPercentileBin
from ..core.db import get_session
from sqlmodel import select

class RunningAnalyzer:
    def __init__(self, request: RunningRequest):
        self.request = request
        self.session = get_session()

    def _load_bins(self, gender: str, age_group: tuple[int, int]) -> List[RunningPercentileBin]:
        stmt = select(RunningPercentileBin).where(
            #RunningPercentileBin.race_id.in_(self.request.target_races),
            RunningPercentileBin.distance == self.request.distance,
            RunningPercentileBin.gender == gender,
            RunningPercentileBin.age_group_start == age_group[0],
            RunningPercentileBin.age_group_end == age_group[1],
        )
        return self.session.exec(stmt).all()

    def _make_histogram(self, bins: List[RunningPercentileBin], age_group: tuple[int, int]) -> HistogramResult:
        if not bins:
            return HistogramResult(bins=[], user_percentile=0.0)

        # calculate total participants
        total = sum(b.count for b in bins if b.count > 0 and b.finish_seconds_max > b.finish_seconds_min)
        if total == 0:
            return HistogramResult(bins=[], user_percentile=0.0)

        # calculate user percentile
        faster = 0.0
        for b in bins:
            if b.count <= 0 or b.finish_seconds_max <= b.finish_seconds_min:
                continue
            if self.request.record_seconds <= b.finish_seconds_min:
                continue
            elif self.request.record_seconds >= b.finish_seconds_max:
                faster += b.count
            else:
                # calculate the portion of the bin that is faster than the user's record
                portion = (self.request.record_seconds - b.finish_seconds_min) / (b.finish_seconds_max - b.finish_seconds_min)
                faster += b.count * portion

        user_percentile = round((faster / total) * 100, 2)

        # make time-based histogram bins
        min_time = min(b.finish_seconds_min for b in bins)
        max_time = max(b.finish_seconds_max for b in bins)
        num_bins = 15
        bin_size = math.ceil((max_time - min_time) / num_bins)

        result_bins: List[HistogramBin] = []

        for i in range(num_bins):
            bin_start = min_time + i * bin_size
            bin_end = bin_start + bin_size
            count = 0.0

            for b in bins:
                if b.count <= 0 or b.finish_seconds_max <= b.finish_seconds_min:
                    continue

                # calculate overlap with the bin
                overlap_start = max(bin_start, b.finish_seconds_min)
                overlap_end = min(bin_end, b.finish_seconds_max)

                if overlap_start < overlap_end:
                    bin_range = b.finish_seconds_max - b.finish_seconds_min
                    overlap = overlap_end - overlap_start
                    portion = overlap / bin_range
                    count += b.count * portion

            percent = round((count / total) * 100, 2) if total > 0 else 0.0
            is_user_bin = bin_start <= self.request.record_seconds < bin_end
            if i == 0 and self.request.record_seconds < bin_end:
                is_user_bin = True
            elif i == num_bins - 1 and self.request.record_seconds >= bin_start:
                is_user_bin = True
            result_bins.append(HistogramBin(
                time_range_start=int(bin_start),
                time_range_end=int(bin_end),
                percent=percent,
                count=int(round(count)),
                is_user_bin=is_user_bin
            ))

        return HistogramResult(
            bins=result_bins,
            user_percentile=user_percentile,
            age_range_start=age_group[0],
            age_range_end=age_group[1]
        )


    # def _make_histogram(self, bins: List[RunningPercentileBin], age_group: tuple[int, int]) -> HistogramResult:
    #     if not bins:
    #         return HistogramResult(bins=[], user_percentile=0.0)

    #     # 1. make synthetic records
    #     synthetic: List[float] = []
    #     for b in bins:
    #         if b.count <= 0 or b.finish_seconds_max == b.finish_seconds_min:
    #             continue
    #         step = (b.finish_seconds_max - b.finish_seconds_min) / b.count
    #         synthetic.extend([b.finish_seconds_min + i * step for i in range(b.count)])

    #     if not synthetic:
    #         return HistogramResult(bins=[], user_percentile=0.0)

    #     # 2. sort synthetic records
    #     synthetic.sort()
    #     total = len(synthetic)

    #     # 3. calculate user percentile
    #     faster = sum(1 for r in synthetic if r < self.request.record_seconds)
    #     user_percentile = round((faster / total) * 100, 2)

    #     # 4. make time-based histogram bins
    #     result_bins: List[HistogramBin] = []

    #     min_time = math.floor(min(synthetic))
    #     max_time = math.ceil(max(synthetic))
    #     num_bins = 15
    #     bin_size = math.ceil((max_time - min_time) / num_bins)

    #     for i in range(num_bins):
    #         bin_start_sec = min_time + i * bin_size
    #         bin_end_sec = bin_start_sec + bin_size

    #         segment = [r for r in synthetic if bin_start_sec <= round(r) < bin_end_sec]
    #         count = len(segment)
    #         percent = round((count / total) * 100, 2) if total > 0 else 0.0

    #         is_user_bin = bin_start_sec <= self.request.record_seconds < bin_end_sec
    #         if i == 0 and self.request.record_seconds < bin_end_sec:
    #             is_user_bin = True
    #         elif i == num_bins - 1 and self.request.record_seconds >= bin_start_sec:
    #             is_user_bin = True

    #         result_bins.append(HistogramBin(
    #             time_range_start=bin_start_sec,
    #             time_range_end=bin_end_sec,
    #             percent=percent,
    #             count=count,
    #             is_user_bin=is_user_bin
    #         ))

    #     return HistogramResult(bins=result_bins, user_percentile=user_percentile, age_range_start=age_group[0], age_range_end=age_group[1])

    def _get_age_group_range(self, age: int) -> tuple[int, int]:
        AGE_GROUPS = [(0, 9)] + [(a, a + 4) for a in range(10, 75, 5)] + [(75, 99)]
        for start, end in AGE_GROUPS:
            if start <= age <= end:
                return (start, end)
        return (75, 99)

    def analyze(self) -> RunningResponse:
        gender_map = {"male": "M", "female": "F"}
        gender_code = gender_map.get(self.request.gender.lower(), "ALL")
        age = self.request.age

        age_group = self._get_age_group_range(age)

        overall_bins = self._load_bins(gender="ALL", age_group=(0, 99))
        gender_bins = self._load_bins(gender=gender_code, age_group=(0, 99))
        gender_age_bins = self._load_bins(gender=gender_code, age_group=age_group)

        return RunningResponse(
            overall=self._make_histogram(overall_bins, age_group),
            by_gender=self._make_histogram(gender_bins, age_group),
            by_gender_age=self._make_histogram(gender_age_bins, age_group)
        )