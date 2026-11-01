
package com.springboot.service;

import java.util.List;
import com.springboot.domain.RaceRecord;

public class ProgressCalculator {

    //전체 레이스 수
    public int getTotalCount(List<RaceRecord> races) {
        return races.size();
    }

    //우승 레이스 수
    public int getWonCount(List<RaceRecord> races) {
        int count = 0;

        for (RaceRecord race : races) {
            if (race.isWon()) {
                count++;
            }
        }

        return count;
    }

    //전관 달성률 계산
    public double getProgress(List<RaceRecord> races) {

        if (races.isEmpty()) {
            return 0.0;
        }

        int total = getTotalCount(races);
        int won = getWonCount(races);

        return (double) won / total * 100;
    }
}