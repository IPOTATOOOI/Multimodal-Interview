package com.example.spr_swcup.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import com.example.spr_swcup.model.QA;

public interface QARepository extends JpaRepository<QA, Integer> {
    List<QA> findByHistoryId(Integer historyId);
}
